"""
This module encapsulates the interactions with the restclients.bridge
"""
import json
import logging
from restclients.models.bridge import BridgeCustomField, BridgeUser
from restclients.bridge.custom_field import new_regid_custom_field
from restclients.bridge.user import add_user, change_uid, replace_uid,\
    delete_user, delete_user_by_id, get_user, get_user_by_id, get_all_users,\
    update_user, restore_user_by_id, restore_user
from restclients.exceptions import DataFailureException
from sis_provisioner.dao import is_using_file_dao
from sis_provisioner.util.log import log_exception


logger = logging.getLogger(__name__)


def _check_user_exists(action, ret_users, uw_bridge_user):
    """
    Check if the uw_bridge_user exists in Bridge.
    :return: the corresponding BridgeUser object.
    """
    if len(ret_users) == 0:
        logger.info("Pre-%s Check %s ==> terminated in Bridge ==> restore",
                    action, uw_bridge_user)
        return _restore(uw_bridge_user)
    logger.info("Pre-%s Check %s ==> user exists in Bridge",
                action, uw_bridge_user)
    return ret_users[0]


def add_bridge_user(uw_bridge_user):
    """
    :param uw_bridge_user: a valid sis_provisioner.models.UwBridgeUser object
    :return: 1) the BridgeUser object (without custom fields)
             2) True if the account already existed
    """
    try:
        user_in_bridge = _check_user_exists("create",
                                            get_user(uw_bridge_user.netid),
                                            uw_bridge_user)
        if user_in_bridge is None:
            # unable to restore the terminated existing user
            logger.error("Can't create %s <== CHECK in Bridge",
                         uw_bridge_user)
        else:
            logger.error("Skip create %s <== user exists in Bridge %s",
                         uw_bridge_user, user_in_bridge)
        return user_in_bridge, True
    except DataFailureException as ex:
        if ex.status != 404:
            raise

    # Create a new account
    bri_user = _process_response(
        "Add Bridge User",
        add_user(_get_bridge_user_to_add(uw_bridge_user)),
        uw_bridge_user)
    return bri_user, False


def change_uwnetid(uw_bridge_user):
    """
    :param uw_bridge_user: a valid UwBridgeUser object
    :return: the returned BridgeUser object
    """
    # Pre-change-uid check:
    if uw_bridge_user.has_bridge_id():
        ret_users = get_user_by_id(uw_bridge_user.bridge_id)
    else:
        ret_users = get_user(uw_bridge_user.prev_netid)

    if len(ret_users) == 0:
        # terminated existing user
        logger.error("Can't change uid %s <== CHECK in Bridge",
                     uw_bridge_user)
        return None
    user_in_bridge = ret_users[0]
    if uw_bridge_user.netid == user_in_bridge.netid:
        logger.info("Skip change uid %s <== Already changed in  Bridge %s",
                    uw_bridge_user, user_in_bridge)
        return user_in_bridge

    if uw_bridge_user.prev_netid != user_in_bridge.netid:
        logger.error("Can't change uid %s <== CHECK Bridge user %s",
                     uw_bridge_user, user_in_bridge)
        return None
    return _change_uid(uw_bridge_user)


def _change_uid(uw_bridge_user):
    """
    :return: the BridgeUser object returned from Bridge
    """
    if uw_bridge_user.has_bridge_id():
        busers = change_uid(uw_bridge_user.bridge_id,
                            uw_bridge_user.netid)
    else:
        busers = replace_uid(uw_bridge_user.prev_netid,
                             uw_bridge_user.netid)

    return _process_response("Change UID", busers, uw_bridge_user)


def delete_bridge_user(user, conditional):
    """
    :param user: a valid BridgeUser or UwBridgeUser object.
    :param conditional: if True, delete only when this user has
                        no learning history.
    :return: True if the user is deleted successfully
    """
    user_in_bridge = get_bridge_user_object(user)
    if user_in_bridge is None:
        logger.info("Skip delete %s <== Already terminated in Bridge", user)
        return True

    if not _uid_matched(user, user_in_bridge):
        regid = get_regid_from_bridge_user(user_in_bridge)
        if regid is not None and user.regid != regid:
            logger.error("Can't delete %s <== CHECK in Bridge %s",
                         user, user_in_bridge)
            return False

    if not conditional or user_in_bridge.no_learning_history():
        if user.bridge_id > 0:
            return delete_user_by_id(user.bridge_id)
        return delete_user(user.netid)

    # try 1. delete the one without learning history and
    #     2. change uid on this account
    logger.error("Can't delete conditionally %s <== CHECK in Bridge %s",
                 user, user_in_bridge)
    return False


def get_all_bridge_users():
    """
    Return a list of (active) BridgeUser objects with custom fields
    """
    return get_all_users()


def get_bridge_user_object(user):
    """
    :param user: a valid BridgeUser or UwBridgeUser object
    :return: a BridgeUser objects with custom fields
    """
    return _process_response("Get Bridge User", get_bridge_user(user), user)


def get_bridge_user(user):
    """
    :param user: a valid BridgeUser or UwBridgeUser object
    :return: a list of BridgeUser objects with custom fields
    """
    if user.has_bridge_id():
        return get_user_by_id(user.bridge_id)

    return get_user(user.netid)


def restore_bridge_user(uw_bridge_user):
    """
    :param uw_bridge_user: a valid UwBridgeUser object
    :return: a BridgeUser objects with custom fields
    """
    user_in_bridge = get_bridge_user_object(uw_bridge_user)
    if user_in_bridge is not None:
        logger.info("Skip restore %s <== exists in Bridge %s",
                    uw_bridge_user, user_in_bridge)
        return user_in_bridge
    return _restore(uw_bridge_user)


def _restore(uw_bridge_user):
    """
    :return: the BridgeUser object returned from Bridge
    """
    if uw_bridge_user.has_bridge_id():
        busers = restore_user_by_id(uw_bridge_user.bridge_id,
                                    no_custom_fields=False)
    else:
        busers = restore_user(uw_bridge_user.netid,
                              no_custom_fields=False)

    return _process_response("Restore Bridge User", busers, uw_bridge_user)


def update_bridge_user(uw_bridge_user):
    """
    :param uw_bridge_user: a valid UwBridgeUser object
    :return: None if updating is not necessary
             True if updated successfully, otherwise False.
    """
    user_in_bridge = _check_user_exists("update",
                                        get_bridge_user(uw_bridge_user),
                                        uw_bridge_user)

    if not _uid_matched(uw_bridge_user, user_in_bridge):
        logger.info("Pre-update check %s ==> change uid on %s",
                    uw_bridge_user, user_in_bridge)
        uw_bridge_user.set_prev_netid(user_in_bridge.netid)
        user_in_bridge = _change_uid(uw_bridge_user)

    if _no_change(uw_bridge_user, user_in_bridge):
        logger.info("Skip updating %s with %s <== NO change",
                    user_in_bridge, uw_bridge_user)
        return None

    new_bri_user = _get_bridge_user_to_upd(uw_bridge_user, user_in_bridge)

    bri_user = _process_response("Update Bridge User %s" % user_in_bridge,
                                 update_user(new_bri_user), uw_bridge_user)
    return _uid_matched(uw_bridge_user, bri_user)


def _new_regid_custom_field(uw_bridge_user):
    return new_regid_custom_field(uw_bridge_user.regid)


def _get_bridge_user_to_add(uw_bridge_user):
    """
    :param uw_bridge_user: a valid UwBridgeUser object
    :return: a BridgeUser object
    """
    user = BridgeUser(netid=uw_bridge_user.netid,
                      email=uw_bridge_user.get_email(),
                      full_name=uw_bridge_user.get_display_name())

    if uw_bridge_user.has_first_name():
        user.first_name = uw_bridge_user.first_name

    if len(uw_bridge_user.last_name) > 1:
        user.last_name = uw_bridge_user.last_name

    user.custom_fields.append(_new_regid_custom_field(uw_bridge_user))
    return user


def _get_bridge_user_to_upd(uw_bridge_user, user_in_bridge):
    """
    :param uw_bridge_user: a valid UwBridgeUser object
    :param user_in_bridge: a valid BridgeUser object
    :return: a BridgeUser object
    """
    user = BridgeUser(bridge_id=user_in_bridge.bridge_id,
                      netid=uw_bridge_user.netid,
                      email=uw_bridge_user.get_email(),
                      full_name=uw_bridge_user.get_display_name())

    if uw_bridge_user.has_first_name() and\
       uw_bridge_user.first_name != user_in_bridge.first_name:
        user.first_name = uw_bridge_user.first_name

    if len(uw_bridge_user.last_name) > 0 and\
       uw_bridge_user.last_name != user_in_bridge.last_name:
        user.last_name = uw_bridge_user.last_name

    if not _custom_field_no_change(uw_bridge_user, user_in_bridge):
        cus_field = _new_regid_custom_field(uw_bridge_user)
        user.custom_fields.append(cus_field)
    return user


def get_regid_value_id(bridge_user):
    if bridge_user.custom_fields is not None and\
       len(bridge_user.custom_fields) > 0:
        for custom_field in bridge_user.custom_fields:
            if custom_field.is_regid():
                return custom_field.value, custom_field.value_id
    return None, None


def get_regid_from_bridge_user(bridge_user):
    regid, value_id = get_regid_value_id(bridge_user)
    return regid


def _custom_field_no_change(uw_bridge_user, user_in_bridge):
    """
    :param uw_bridge_user: a valid UwBridgeUser object
    :param user_in_bridge: a valid BridgeUser object
    :return: True if the custom fields have the same values
    """
    regid = get_regid_from_bridge_user(user_in_bridge)
    return (regid is not None and uw_bridge_user.regid == regid)


def _no_change(uw_bridge_user, user_in_bridge):
    """
    :param uw_bridge_user: a valid UwBridgeUser object
    :param user_in_bridge: a valid BridgeUser object
    :return: True if the attributes have the same values
    """
    return (uw_bridge_user.netid == user_in_bridge.netid and
            uw_bridge_user.bridge_id == user_in_bridge.bridge_id and
            uw_bridge_user.get_email() == user_in_bridge.email and
            uw_bridge_user.get_display_name() == user_in_bridge.full_name and
            uw_bridge_user.last_name == user_in_bridge.last_name and
            _custom_field_no_change(uw_bridge_user, user_in_bridge))


def _process_response(action, ret_users, uw_bridge_user):
    if len(ret_users) == 0:
        logger.info("%s %s ==> user terminated in Bridge",
                    action, uw_bridge_user)
        return None

    if len(ret_users) > 1:
        logger.warning("%s %s ==> returned multiple users: %s",
                       action, uw_bridge_user, ",".join(ret_users))
    return ret_users[0]


def _uid_matched(uw_bridge_user, ret_bridge_user):
    return (ret_bridge_user is not None and
            uw_bridge_user.netid == ret_bridge_user.netid)
