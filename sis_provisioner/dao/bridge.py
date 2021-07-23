# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
This module encapsulates the interactions with uw_bridge.users
"""

import logging
import traceback
from uw_bridge.models import BridgeUserRole
from uw_bridge.users import Users
from sis_provisioner.dao import DataFailureException
from sis_provisioner.util.log import log_exception


logger = logging.getLogger(__name__)


class BridgeUsers(Users):
    """
    These two methods are defined in super class:
    add_user(self, bridge_user)
    get_all_users()
    update_user(self, bridge_user)
    """

    def __init__(self):
        super(BridgeUsers, self).__init__()

    def change_uwnetid(self, uw_account):
        """
        :param uw_account: a valid UwAccount object
        :return: the BridgeUser object returned from Bridge
        """
        if uw_account.has_bridge_id():
            return self.change_uid(uw_account.bridge_id, uw_account.netid)
        else:
            return self.replace_uid(uw_account.prev_netid, uw_account.netid)

    def delete_bridge_user(self, bridge_user):
        """
        :param: a valid BridgeUser object of an existing account in Bridge
        :return: True if the user is deleted successfully
        """
        if bridge_user.has_bridge_id():
            return self.delete_user_by_id(bridge_user.bridge_id)
        return self.delete_user(bridge_user.netid)

    def get_user_by_bridgeid(self, id):
        """
        if exists any account: returns a valid BridgeUser object
        if not exists: None
        """
        try:
            return self.get_user_by_id(id, include_deleted=True)
        except DataFailureException as ex:
            if ex.status == 404:
                # the user not exists in Bridge
                return None
            log_exception(logger, "get_user_by_bridgeid({0})".format(id),
                          traceback.format_exc(chain=False))
            raise

    def get_user_by_uwnetid(self, netid):
        """
        If exists an active account: returns a valid BridgeUser object
        Otherwise returns None
        """
        try:
            return self.get_user(netid)
            # include_course_summary=True,
            # include_manager=True,
            # not include deleted
        except DataFailureException as ex:
            if ex.status == 404:
                return None
            log_exception(logger,
                          "get_user_by_uwnetid('{0}')".format(netid),
                          traceback.format_exc(chain=False))
            raise

    def get_all_authors(self):
        try:
            return self.get_all_users(role_id=self.user_roles.get_role_id(
                BridgeUserRole.AUTHOR_NAME))
        except DataFailureException:
            log_exception(logger, "get_all_authors",
                          traceback.format_exc(chain=False))
            raise

    def restore_bridge_user(self, uw_account):
        """
        :param uw_account: a valid UwAccount object
        :return: a BridgeUser objects with custom fields
        :except DataFailureException: if not found the account or failed
        """
        if uw_account.has_bridge_id():
            buser = self.restore_user_by_id(uw_account.bridge_id)
            if buser is not None:
                return buser

        bridge_user = self.restore_user(uw_account.netid)
        if bridge_user is not None:
            uw_account.set_bridge_id(bridge_user.bridge_id)
        return bridge_user
