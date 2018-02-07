"""
The Member class encapsulates the interactions
with the UW Group API resource
"""

import logging
from uw_gws import GWS
from sis_provisioner.util.log import log_resp_time, Timer


logger = logging.getLogger(__name__)
UW_GROUP = "uw_member"
UW_AFFI_GROUP = "uw_affiliation_affiliate-employee"
gws = GWS()


def get_members_of_group(group_id):
    """
    Returns a list of uw_gws.models.GroupMember objects
    """
    action = 'get_members of group %s' % group_id
    timer = Timer()
    try:
        return gws.get_effective_members(group_id)
    finally:
        log_resp_time(logger, action, timer)


def get_uw_members():
    """
    Returns a list of uwnetids in the "uw_member" Group
    """
    ret_list = []
    for gm in get_members_of_group(UW_GROUP):
        if gm.is_uwnetid() and gm.name is not None and len(gm.name) > 0:
            ret_list.append(gm.name)

    return ret_list


def get_affiliate_employees():
    """
    Returns a list of uwnetids in the "uw_member" Group
    """
    ret_list = []
    for gm in get_members_of_group(UW_AFFI_GROUP):
        if gm.is_uwnetid() and gm.name is not None and len(gm.name) > 0:
            ret_list.append(gm.name)

    return ret_list


def get_potential_users():
    return get_uw_members() + get_affiliate_employees()


def is_qualified_user(uwnetid):
    return is_uw_member(uwnetid) or is_affiliate_employee(uwnetid)


def is_uw_member(uwnetid):
    """
    Return True if the user netid is an effective member of the uw_member group
    """
    return (uwnetid in get_uw_members())


def is_affiliate_employee(uwnetid):
    """
    Return True if the user netid is an effective member of
    the uw_affiliation_affiliate-employee group
    """
    return (uwnetid in get_affiliate_employees())
