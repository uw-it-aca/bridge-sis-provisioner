"""
The BridgeWorker class will apply actions on the user account in Bridge
via the Bridge APIs.
"""

import logging
import traceback
from uw_bridge.models import BridgeUser, BridgeCustomField
from sis_provisioner.dao.bridge import BridgeUsers
from sis_provisioner.account_managers import (
    get_email, get_full_name, normalize_name, get_regid)
from sis_provisioner.account_managers.worker import Worker


logger = logging.getLogger(__name__)


class BridgeWorker(Worker):

    def __init__(self):
        super(BridgeWorker, self).__init__(logger)
        self.bridge = BridgeUsers()
        self.total_deleted_count = 0
        self.total_netid_changes_count = 0
        self.total_new_users_count = 0
        self.total_restored_count = 0
        self.total_updated_count = 0

    def _uid_matched(self, uw_account, ret_bridge_user):
        return (ret_bridge_user is not None and
                ret_bridge_user.netid == uw_account.netid)

    def add_new_user(self, uw_account, person):
        action = "CREATE in Bridge: {0}".format(uw_account.netid)
        try:
            bridge_account = self.bridge.add_user(
                self.get_bridge_user_to_add(person))

            if self._uid_matched(uw_account, bridge_account):
                uw_account.set_bridge_id(bridge_account.bridge_id)
                self.total_new_users_count += 1
                logger.info("{0} ==> {1}".format(
                    action, bridge_account.__str__(orig=False)))
                return
            self.append_error("Unmatched UID {0}\n".format(action))
        except Exception as ex:
            self.handle_exception(action, ex, traceback)

    def delete_user(self, bridge_acc):
        action = "DELETE from Bridge {0}".format(bridge_acc)
        try:
            if self.bridge.delete_bridge_user(bridge_acc):
                self.total_deleted_count += 1
                logger.info(action)
                return True
            self.append_error("Error {0}\n".format(action))
        except Exception as ex:
            self.handle_exception(action, ex, traceback)
        return False

    def restore_user(self, uw_account):
        action = "RESTORE in Bridge {0}".format(uw_account)
        try:
            bridge_account = self.bridge.restore_bridge_user(uw_account)
            if bridge_account is not None:
                uw_account.set_restored()
                self.total_restored_count += 1
                logger.info("{0} ==> {1}".format(
                    action, bridge_account.__str__(orig=False)))
                return bridge_account
        except Exception as ex:
            self.handle_exception(action, ex, traceback)
        return None

    def update_uid(self, uw_account):
        action = "CHANGE UID from {0} to {1}".format(
            uw_account.prev_netid, uw_account.netid)
        bridge_account = self.bridge.change_uwnetid(uw_account)
        if self._uid_matched(uw_account, bridge_account):
            self.total_netid_changes_count += 1
            logger.info("{0} ==> {1}".format(
                action, bridge_account.__str__(orig=False)))
            return
        self.append_error("Unmatched UID {0}\n".format(action))

    def update_user(self, bridge_account, uw_account, person):
        user_data = self.get_bridge_user_to_upd(person, bridge_account)
        action = "UPDATE in Bridge: {0}".format(bridge_account.netid)
        try:
            if (uw_account.netid_changed() and
                    bridge_account.netid == uw_account.prev_netid):
                self.update_uid(uw_account)

            updated_bri_acc = self.bridge.update_user(user_data)
            if self._uid_matched(uw_account, updated_bri_acc):
                uw_account.set_updated()
                self.total_updated_count += 1
                logger.info("{0} ==> {1}".format(
                    action, bridge_account.__str__(orig=False)))
                return
            self.append_error("Unmatched UID {0}\n".format(action))
        except Exception as ex:
            self.handle_exception(action, ex, traceback)

    def get_new_user_count(self):
        return self.total_new_users_count

    def get_netid_changed_count(self):
        return self.total_netid_changes_count

    def get_restored_count(self):
        return self.total_restored_count

    def get_deleted_count(self):
        return self.total_deleted_count

    def get_updated_count(self):
        return self.total_updated_count

    def get_bridge_user_to_add(self, person):
        """
        :param person: a valid Person object
        :return: a BridgeUser object
        """
        user = BridgeUser(netid=person.uwnetid,
                          email=get_email(person),
                          full_name=get_full_name(person),
                          first_name=normalize_name(person.first_name),
                          last_name=normalize_name(person.surname))
        self.add_regid_custom_field(user, person.uwregid)
        return user

    def get_bridge_user_to_upd(self, person, bridge_account):
        """
        :param person: a valid Person object
        :param bridge_account: a valid BridgeUser object
        :return: a BridgeUser object
        """
        user = BridgeUser(
            bridge_id=bridge_account.bridge_id,
            netid=person.uwnetid,
            email=get_email(person),
            full_name=get_full_name(person),
            first_name=normalize_name(person.first_name),
            last_name=normalize_name(person.surname))

        if self.not_changed_regid(person.uwregid, bridge_account) is False:
            self.add_regid_custom_field(user, person.uwregid)
        return user

    def not_changed_regid(self, uwregid, bridge_account):
        return uwregid is not None and uwregid == get_regid(bridge_account)

    def add_regid_custom_field(self, user, regid):
        user.custom_fields[BridgeCustomField.REGID_NAME] = \
            self.create_custom_field(BridgeCustomField.REGID_NAME, regid)

    def create_custom_field(self, field_name, value):
        return self.bridge.custom_fields.new_custom_field(field_name, value)
