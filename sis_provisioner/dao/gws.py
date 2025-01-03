# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging
from sis_provisioner.dao import DataFailureException, get_dt_from_now
from uw_gws import GWS
from sis_provisioner.util.log import log_resp_time, Timer
from sis_provisioner.util.settings import get_author_group_name

logger = logging.getLogger(__name__)
EMP_GROUPS = [
    "uw_employee",
    "uw_affiliation_affiliate-employee",
    "uw_affiliation_uw-medicine-workforce",
    "uw_affiliation_uw-medicine-affiliate",
    "uw_affiliation_wwami-medical-resident"
    ]
STU_GROUPS = [
    "uw_student"
    ]
CUSTOM_GROUP = "u_bridgeap_tempusers"


def _add_netids_to_mset(members, member_set):
    for gm in members:
        if gm.is_uwnetid() and gm.name is not None and len(gm.name):
            member_set.add(gm.name)


def _get_start_timestamp(duration):
    return int(get_dt_from_now(duration).timestamp())


class Gws(GWS):

    def __init__(self):
        super(Gws, self).__init__()
        self._setup()

    def _setup(self):
        """
        Throw DataFailureException
        """
        timer = Timer()
        self.hrp_user_set = self._get_user_set(EMP_GROUPS)
        self.stu_user_set = self._get_user_set(STU_GROUPS)
        self.temp_user_set = self._get_temp_users()
        self.base_users = self.hrp_user_set.union(self.stu_user_set)
        self.potential_users = self.base_users.union(self.temp_user_set)
        log_resp_time(logger, "load user sets", timer)

    def _get_user_set(self, groupid_list):
        """
        return a set of uwnetids in groupid_list
        throw DataFailureException
        """
        member_set = set()
        self._joint_groups_members(groupid_list, member_set)
        return member_set

    def _joint_groups_members(self, groups, member_set):
        for gr in groups:
            _add_netids_to_mset(
                self._get_members_of_group(gr), member_set)

    def _get_temp_users(self):
        """
        return a set of uwnetids in the temp user groups
        throw DataFailureException
        """
        temp_user_groups = []
        for gm in self._get_members_of_group(CUSTOM_GROUP):
            if gm.is_group() and gm.name:
                temp_user_groups.append(gm.name)
        return self._get_user_set(temp_user_groups)

    def _get_members_of_group(self, group_id):
        """
        Returns a list of GroupMember objects
        except: DataFailureException
        """
        timer = Timer()
        action = "get_members({0})".format(group_id)
        try:
            return self.get_members(group_id)
        finally:
            log_resp_time(logger, action, timer)

    def get_bridge_authors(self):
        return self._get_user_set([get_author_group_name()])

    def _get_member_changes(self, group_id, start_timestamp):
        """
        Returns a list of uwnetids of the added within the given duration
        start_timestamp: in seconds
        except: DataFailureException
        """
        timer = Timer()
        action = f"get_group_history({group_id}, {start_timestamp})"
        try:
            return self.get_group_history(
                group_id, activity="membership", start=start_timestamp)
        finally:
            log_resp_time(logger, action, timer)

    def get_changed_members(self, group_id, duration):
        """
        Returns a list of uwnetids of the added within the given duration
        duration: in minutes
        except: DataFailureException
        """
        users_added = set()
        users_deleted = set()
        changes = self._get_member_changes(
            group_id, _get_start_timestamp(duration))
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

    def get_added_members(self, duration):
        """
        duration: in minutes
        return a set of uwnetids
        """
        timer = Timer()
        user_set = set()
        for gr in EMP_GROUPS + STU_GROUPS:
            try:
                users_added, users_deleted = self.get_changed_members(
                    gr, duration)
                user_set = user_set.union(users_added)
            except DataFailureException as ex:
                logger.error(ex)
        log_resp_time(logger, "get_added_members", timer)
        return user_set

    def get_deleted_members(self, duration):
        """
        duration: in minutes
        return a set of uwnetids
        """
        timer = Timer()
        user_set = set()
        for gr in EMP_GROUPS + STU_GROUPS:
            try:
                users_added, users_deleted = self.get_changed_members(
                    gr, duration)
                user_set = user_set.union(users_deleted)
            except DataFailureException as ex:
                logger.error(ex)
        log_resp_time(logger, "get_deleted_members", timer)
        return user_set
