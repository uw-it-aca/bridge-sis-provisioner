"""
This module encapsulates the interactions with the restclients.bridge
"""

import logging
from restclients.models.bridge import BridgeCustomField, BridgeUser
from restclients.bridge.custom_field import new_regid_custom_field
from restclients.bridge.user import add_user, change_uid, replace_uid,\
    delete_user, delete_user_by_id, get_user, get_user_by_id, get_all_users,\
    update_user, restore_user_by_id, restore_user, get_regid_from_custom_fields
from restclients.exceptions import DataFailureException
from sis_provisioner.util.log import log_exception


logger = logging.getLogger(__name__)


def add_bridge_user(uw_bridge_user):
    """
    @param: uw_bridge_user a valid sis_provisioner.models.UwBridgeUser object
    Return a list of BridgeUser objects with custom fields
    """
    return _log_result(
        add_user(_get_bridge_user_to_add(uw_bridge_user)),
        "add bridge user: %s" % uw_bridge_user)


def delete_bridge_user(bridge_user, conditional=True):
    """
    @param: bridge_user a valid BridgeUser or UwBridgeUser object.
    @param: if conditional is True, delete only when this user has
            no learning history.
    Return True if the user is deleted successfully
    """
    if not conditional or _no_learning_history(bridge_user):
        if bridge_user.bridge_id > 0:
            return delete_user_by_id(bridge_user.bridge_id)
        return delete_user(bridge_user.netid)

    if conditional:
        logger.error(
            "Can't delete %s, having learning history" % bridge_user.netid)
    return False


def _no_learning_history(bridge_user):
    """
    Check the user's learning history and return True if the user
    has zero completed course.
    """
    ret_users = get_bridge_user(bridge_user)
    if len(ret_users) == 1:
        user = ret_users[0]
        return user.no_learning_history()
    return False


def change_uwnetid(uw_bridge_user):
    """
    @param: uw_bridge_user a valid UwBridgeUser object
    Return a list of BridgeUser objects without custom fields
    """
    # update the uid first so the correct UID is set
    if uw_bridge_user.bridge_id > 0:
        busers = change_uid(uw_bridge_user.bridge_id,
                            uw_bridge_user.netid)
    else:
        busers = replace_uid(uw_bridge_user.prev_netid,
                             uw_bridge_user.netid)
    return _log_result(busers,
                       "change_uid: %s --> %s" % (uw_bridge_user.prev_netid,
                                                  uw_bridge_user.netid))


def get_bridge_user_object(uw_bridge_user):
    """
    @param: uw_bridge_user a valid UwBridgeUser object
    Return a list of BridgeUser objects with custom fields
    """
    ret_users = get_bridge_user(uw_bridge_user)
    count = len(ret_users)
    if count > 1:
        logger.error(
            "get_bridge_user (%s) expect 1 user returns %d users: %s" %
            (uw_bridge_user.netid, count, ",".join(ret_users)))
    return ret_users[0] if count > 0 else None


def get_bridge_user(uw_bridge_user):
    """
    @param: uw_bridge_user a valid UwBridgeUser object
    Return a list of BridgeUser objects with custom fields
    """
    if uw_bridge_user.bridge_id > 0:
        bridge_id = uw_bridge_user.bridge_id
        return _log_result(get_user_by_id(bridge_id),
                           "get bridge user: %s" % bridge_id)
    uwnetid = uw_bridge_user.netid
    return _log_result(get_user(uwnetid),
                       "get bridge user: %s" % uwnetid)


def get_all_bridge_users():
    """
    Return a list of (active) BridgeUser objects with custom fields
    """
    return _log_result(get_all_users(), "get all bridge users")


def get_regid_from_bridge_user(bridge_user):
    return get_regid_from_custom_fields(bridge_user.custom_fields)


def restore_bridge_user(uw_bridge_user):
    """
    Return a list of BridgeUser objects without custom fields
    """
    if uw_bridge_user.bridge_id > 0:
        bridge_id = uw_bridge_user.bridge_id
        return _log_result(restore_user_by_id(bridge_id),
                           "restore bridge user: %s" % bridge_id)
    uwnetid = uw_bridge_user.netid
    return _log_result(restore_user(uwnetid),
                       "restore bridge user: %s" % uwnetid)


def update_bridge_user(uw_bridge_user):
    """
    @param: uw_bridge_user a valid UwBridgeUser object
    Return a list of BridgeUser objects with custom fields
    """
    user_in_bridge = get_bridge_user_object(uw_bridge_user)
    if user_in_bridge is None:
        logger.error("update_bridge_user (%s) find no user in Bridge" %
                     uw_bridge_user)
        return None
    new_bri_user = _get_bridge_user_to_upd(uw_bridge_user,
                                           user_in_bridge)
    return _log_result(update_user(new_bri_user),
                       "update bridge user: %s" % uw_bridge_user)


def _new_regid_custom_field(uw_bridge_user):
    return new_regid_custom_field(uw_bridge_user.regid)


def _get_bridge_user_to_add(uw_bridge_user):
    """
    @param: uw_bridge_user a valid UwBridgeUser object
    @return: a BridgeUser object to be added in Bridge
    """
    user = BridgeUser()
    user.netid = uw_bridge_user.netid
    user.full_name = uw_bridge_user.get_display_name()
    user.first_name = uw_bridge_user.first_name
    user.last_name = uw_bridge_user.last_name
    user.email = uw_bridge_user.get_email()
    user.custom_fields.append(_new_regid_custom_field(uw_bridge_user))
    return user


def _get_bridge_user_to_upd(uw_bridge_user, user_in_bridge):
    """
    @param: uw_bridge_user a valid UwBridgeUser object
    @param: user_in_bridge a valid BridgeUser object
    @return: a BridgeUser object to be udpate in Bridge
    """
    user = BridgeUser()
    if uw_bridge_user.bridge_id > 0:
        user.bridge_id = uw_bridge_user.bridge_id
    else:
        if user_in_bridge.bridge_id:
            user.bridge_id = user_in_bridge.bridge_id

    user.netid = uw_bridge_user.netid
    user.email = uw_bridge_user.get_email()
    user.full_name = uw_bridge_user.get_display_name()
    if uw_bridge_user.has_first_name():
        user.first_name = uw_bridge_user.first_name
    else:
        user.first_name = user_in_bridge.first_name

    if uw_bridge_user.last_name is not None:
        user.last_name = uw_bridge_user.last_name
    else:
        user.last_name = user_in_bridge.last_name

    for ori_cus_fie in user_in_bridge.custom_fields:
        if ori_cus_fie.is_regid():
            cus_fie = _new_regid_custom_field(uw_bridge_user)
            if not uw_bridge_user.regid_changed() and\
                    ori_cus_fie.value == uw_bridge_user.regid:
                cus_fie.value_id = ori_cus_fie.value_id
            # if the existing value_id not presented,
            # replace the custom field value
            user.custom_fields.append(cus_fie)
    return user


def _log_result(busers, action):
    logger.info("%s returned %d users" % (action, len(busers)))
    return busers
