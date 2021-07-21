# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
The functions here interact with uw_gws
"""

import logging
from sis_provisioner.dao import (
    DataFailureException, read_gws_cache_file, write_gws_cache_file)
from uw_gws import GWS
from sis_provisioner.util.log import log_resp_time, Timer
from sis_provisioner.util.settings import (
    get_author_group_name, get_gws_cache_path)


logger = logging.getLogger(__name__)
UW_GROUPS = ["uw_member", "uw_affiliate", "u_bridgeap_tempusers"]
gws = GWS()


def get_members_of_group(group_id):
    """
    Returns a list of uw_gws.GroupMember objects
    except: DataFailureException
    """
    timer = Timer()
    action = "get_effective_members('{0}')".format(group_id)
    try:
        return gws.get_effective_members(group_id)
    finally:
        log_resp_time(logger, action, timer)
    return None


def append_netids_to_list(members, user_set):
    if members is not None and len(members) > 0:
        for gm in members:
            if gm.is_uwnetid() and gm.name is not None and len(gm.name) > 0:
                if gm.name not in user_set:
                    user_set.add(gm.name)


def get_potential_users():
    """
    return a set of uwnetids
    """
    timer = Timer()
    user_set = set()
    for gr in UW_GROUPS:
        append_netids_to_list(get_members_of_group(gr), user_set)
    log_resp_time(logger, "get_potential_users", timer)
    return user_set


def get_bridge_authors():
    user_set = set()
    append_netids_to_list(get_members_of_group(get_author_group_name()),
                          user_set)
    return user_set


def get_member_updates(current_user_set):
    """
    return a set of uwnetids
    """
    path = get_gws_cache_path()
    last_user_set = read_gws_cache_file(path)
    write_gws_cache_file(path, current_user_set)
    return current_user_set - last_user_set
