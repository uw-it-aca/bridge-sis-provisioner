"""
The Member class encapsulates the interactions
with the UW Group API resource
"""

import logging
from restclients.gws import GWS
from sis_provisioner.util.time_helper import Timer
from sis_provisioner.util.log import log_resp_time


logger = logging.getLogger(__name__)
UW_GROUP = "uw_member"
gws = GWS()


def get_members_of_group(group_id):
    """
    Returns a list of restclients.models.gws.GroupMember objects
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
        if gm.is_uwnetid():
            ret_list.append(gm.name)

    return ret_list
