"""
This module encapsulates the interactions with the restclients.bridge
"""

import logging
from restclients.models.bridge import BridgeCustomField, BridgeUser
from restclients.bridge.custom_field import new_regid_custom_field
from restclients.bridge.user import add_user, change_uid, replace_uid,\
    delete_user, delete_user_by_id, get_user, get_user_by_id, get_all_users,\
    update_user, restore_user_by_id, restore_user
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


def delete_bridge_user(bridge_user):
    """
    @param: bridge_user a valid BridgeUser or UwBridgeUser object
    Return True if the user is deleted successfully
    """
    if bridge_user.bridge_id:
        return delete_user_by_id(bridge_user.bridge_id)
    return delete_user(bridge_user.netid)


def change_uwnetid(uw_bridge_user):
    """
    @param: uw_bridge_user a valid UwBridgeUser object
    Return a list of BridgeUser objects without custom fields
    """
    # update the uid first so the correct UID is set
    if uw_bridge_user.bridge_id:
        busers = change_uid(uw_bridge_user.bridge_id,
                            uw_bridge_user.netid)
    else:
        busers = replace_uid(uw_bridge_user.prev_netid,
                             uw_bridge_user.netid)
    return _log_result(busers,
                       "change_uid: %s --> %s" % (uw_bridge_user.prev_netid,
                                                  uw_bridge_user.netid))


def get_bridge_user(uw_bridge_user, include_course_summary=False):
    """
    @param: uw_bridge_user a valid UwBridgeUser object
    Return a list of BridgeUser objects with custom fields
    """
    if uw_bridge_user.bridge_id:
        bridge_id = uw_bridge_user.bridge_id
        return _log_result(get_user_by_id(bridge_id,
                                          include_course_summary),
                           "get bridge user: %s" % bridge_id)
    uwnetid = uw_bridge_user.netid
    return _log_result(get_user(uwnetid,
                                include_course_summary),
                       "get bridge user: %s" % uwnetid)


def get_all_bridge_users(include_course_summary=False):
    """
    Return a list of BridgeUser objects with custom fields
    """
    return _log_result(get_all_users(),
                       "get all bridge users")


def restore_bridge_user(uw_bridge_user):
    """
    Return a list of BridgeUser objects without custom fields
    """
    if uw_bridge_user.bridge_id:
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
    user_in_bridge = None
    existing_bridge_users = get_bridge_user(uw_bridge_user)
    if len(existing_bridge_users) > 0:
        user_in_bridge = existing_bridge_users[0]
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
    if uw_bridge_user.bridge_id:
        user.bridge_id = uw_bridge_user.bridge_id
    else:
        if user_in_bridge.bridge_id:
            user.bridge_id = user_in_bridge.bridge_id

    user.netid = uw_bridge_user.netid
    user.email = uw_bridge_user.get_email()
    user.full_name = uw_bridge_user.get_display_name()
    if uw_bridge_user.first_name is not None:
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
