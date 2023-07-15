# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
The functions here interact with uw_gws
"""

import logging
from sis_provisioner.models import get_now
from sis_provisioner.dao import DataFailureException, get_dt_from_now
from uw_gws import GWS
from sis_provisioner.util.log import log_resp_time, Timer
from sis_provisioner.util.settings import get_author_group_name


logger = logging.getLogger(__name__)
BASE_GROUPS = [
    "uw_employee",
    "uw_affiliation_affiliate-employee",
    "uw_affiliation_uw-medicine-workforce",
    "uw_affiliation_uw-medicine-affiliate",
    "uw_affiliation_wwami-medical-resident",
    "uw_student"
    ]
GROUPS_TO_ADD = [
    # "uw_student"
    ]
CUSTOM_GROUP = "u_bridgeap_tempusers"
gws = GWS()


def get_members_of_group(group_id):
    """
    Returns a list of uw_gws.GroupMember objects
    except: DataFailureException
    """
    timer = Timer()
    action = "get_members_of_group({0})".format(group_id)
    try:
        if group_id.startswith("uw_"):
            return gws.get_members(group_id)
        return gws.get_effective_members(group_id)
    finally:
        log_resp_time(logger, action, timer)
    return None


def append_netids_to_list(members, member_set):
    if members is not None and len(members) > 0:
        for gm in members:
            if gm.is_uwnetid() and gm.name is not None and len(gm.name):
                member_set.add(gm.name)


def joint_groups_members(groups, member_set):
    for gr in groups:
        append_netids_to_list(get_members_of_group(gr), member_set)


def get_potential_users():
    """
    return a set of uwnetids
    """
    timer = Timer()
    member_set = set()
    joint_groups_members([CUSTOM_GROUP] + BASE_GROUPS, member_set)
    log_resp_time(logger, "get_potential_users", timer)
    return member_set


def get_additional_users():
    """
    return a set of uwnetids
    """
    timer = Timer()
    member_set = set()
    joint_groups_members([CUSTOM_GROUP] + GROUPS_TO_ADD, member_set)
    log_resp_time(logger, "get_additional_users", timer)
    return member_set


def get_bridge_authors():
    member_set = set()
    append_netids_to_list(
        get_members_of_group(get_author_group_name()), member_set)
    return member_set


def _get_member_changes(group_id, start_timestamp):
    """
    Returns a list of uwnetids of the added within the given duration
    start_timestamp: in seconds
    except: DataFailureException
    """
    timer = Timer()
    action = "get_group_history({}, {})".format(group_id, start_timestamp)
    try:
        return gws.get_group_history(
            group_id, activity="membership", start=start_timestamp)
    finally:
        log_resp_time(logger, action, timer)
    return None


def _get_start_timestamp(duration):
    return int(get_dt_from_now(duration).timestamp())


def get_changed_members(group_id, duration):
    """
    Returns a list of uwnetids of the added within the given duration
    duration: in minutes
    except: DataFailureException
    """
    users_added = set()
    users_deleted = set()
    changes = _get_member_changes(group_id, _get_start_timestamp(duration))
    if changes:
        for c in changes:
            if c.is_add_member():
                if c.member_uwnetid in users_deleted:
                    users_deleted.remove(c.member_uwnetid)
                else:
                    users_added.add(c.member_uwnetid)
            elif c.is_delete_member():
                if c.member_uwnetid in users_added:
                    users_added.remove(c.member_uwnetid)
                else:
                    users_deleted.add(c.member_uwnetid)
    return users_added, users_deleted


def get_added_members(duration):
    """
    duration: in minutes
    return a set of uwnetids
    """
    timer = Timer()
    user_set = set()
    for gr in BASE_GROUPS:
        try:
            users_added, users_deleted = get_changed_members(gr, duration)
            user_set = user_set.union(users_added)
        except DataFailureException as ex:
            logger.error(ex)
    log_resp_time(logger, "get_added_members", timer)
    return user_set


def get_deleted_members(duration):
    """
    duration: in minutes
    return a set of uwnetids
    """
    timer = Timer()
    user_set = set()
    for gr in BASE_GROUPS:
        try:
            users_added, users_deleted = get_changed_members(gr, duration)
            user_set = user_set.union(users_deleted)
        except DataFailureException as ex:
            logger.error(ex)
    log_resp_time(logger, "get_deleted_members", timer)
    return user_set
