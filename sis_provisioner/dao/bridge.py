"""
This module encapsulates the interactions with the uw_bridge
"""

import logging
import traceback
from uw_bridge.user import (
    add_user, change_uid, replace_uid, delete_user, delete_user_by_id,
    get_user, get_user_by_id, get_all_users, update_user,
    restore_user_by_id, restore_user, get_regid_from_custom_fields)
from sis_provisioner.dao import DataFailureException
from sis_provisioner.util.log import log_exception, log_resp_time, Timer


logger = logging.getLogger(__name__)


def add_bridge_user(bridge_user):
    """
    :param bridge_user: a valid BridgeUser object
    :return: the BridgeUser object (without custom fields)
    """
    return _process_response("add_bridge_user({0})".format(bridge_user),
                             add_user(bridge_user))


def change_uwnetid(uw_account):
    """
    :param uw_account: a valid UwAccount object
    :return: the BridgeUser object returned from Bridge
    """
    if uw_account.has_bridge_id():
        busers = change_uid(uw_account.bridge_id, uw_account.netid)
    else:
        busers = replace_uid(uw_account.prev_netid, uw_account.netid)
    return _process_response("change_uwnetid({0})".format(uw_account), busers)


def delete_bridge_user(bridge_user):
    """
    :param: a valid BridgeUser object of an existing account in Bridge
    :return: True if the user is deleted successfully
    """
    if bridge_user.bridge_id > 0:
        return delete_user_by_id(bridge_user.bridge_id)
    return delete_user(bridge_user.netid)


def get_all_bridge_users():
    """
    Return a list of active BridgeUser objects with custom fields
    """
    timer = Timer()
    action = "get_all_bridge_users"
    try:
        return get_all_users()
    except Exception:
        log_exception(logger, action, traceback.format_exc(chain=False))
        raise
    finally:
        log_resp_time(logger, action, timer)


def get_user_by_bridgeid(id):
    """
    if exists an active account: returns True, a valid BridgeUser object
    if exists a terminated account: True, None
    if not exists: False, None
    """
    try:
        bridge_user = _process_response(
            "get_user_by_bridgeid({0})".format(id), get_user_by_id(id))
        return True, bridge_user
    except DataFailureException as ex:
        log_exception(logger, "get_user_by_bridgeid({0})".format(id),
                      traceback.format_exc(chain=False))
        if ex.status == 404:
            # the user not exists in Bridge
            return False, None
        raise


def get_user_by_uwnetid(netid, exclude_deleted=True):
    """
    if exists an active account: returns True, a valid BridgeUser object
    if exists a terminated account: True, None
    if not exists: False, None
    """
    try:
        bridge_user = _process_response(
            "get_user_by_uwnetid('{0}')".format(netid), get_user(netid))
        return True, bridge_user
    except DataFailureException as ex:
        log_exception(logger,
                      "get_user_by_uwnetid('{0}')".format(netid),
                      traceback.format_exc(chain=False))
        if ex.status == 404:
            # the user not exists in Bridge
            return False, None
        raise


def get_regid_from_bridge_user(bridge_user):
    if bridge_user.custom_fields is not None and\
       len(bridge_user.custom_fields) > 0:
        return get_regid_from_custom_fields(bridge_user.custom_fields)
    return None


def restore_bridge_user(uw_account):
    """
    :param uw_account: a valid UwAccount object
    :return: a BridgeUser objects with custom fields
    :except DataFailureException: if not found the account or failed
    """
    if uw_account.has_bridge_id():
        buser = _process_response(
            "restore_bridge_user_by_ridgeid({0})".format(uw_account),
            restore_user_by_id(uw_account.bridge_id, no_custom_fields=False))
        if buser is not None:
            return buser

    bridge_user = _process_response(
        "restore_bridge_user({0})".format(uw_account),
        restore_user(uw_account.netid, no_custom_fields=False))
    if bridge_user is not None:
        uw_account.set_bridge_id(bridge_user.bridge_id)
    return bridge_user


def update_bridge_user(bridge_user):
    """
    :param account_data: a valid BridgeUser object
    :return: the BridgeUser object in the response
    :except DataFailureException: if not found the account or failed
    """
    return _process_response(
        "update_bridge_user({0})".format(bridge_user),
        update_user(bridge_user))


def _process_response(action, bridge_users):
    if len(bridge_users) == 0:
        logger.info("{0} found a deleted user in Bridge".format(action))
        return None

    if len(bridge_users) > 1:
        logger.warning(
            "{0} found multiple users in Bridge: {1}".format(
                action, ", ".join(bridge_users)))
    return bridge_users[0]
