"""
The functions here interact with uw_gws
"""

import logging
from sis_provisioner.dao import DataFailureException
from uw_gws import GWS
from sis_provisioner.util.log import log_resp_time, Timer


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
