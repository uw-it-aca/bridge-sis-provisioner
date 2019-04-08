"""
This class will load all the users in gws uw_member, uw_aafiliate groups.
Check against PWS Person.
1. Add new user account in Db (and to Bridge)
2. Update existing account for netid, name, email, regid  changes.
3. Restore disabled/terminated account
4. Terminate Bridge account with a prior netid
"""

import logging
import traceback
from uw_bridge.models import BridgeUser
from sis_provisioner.dao.bridge import (
    get_user_by_bridgeid, get_user_by_uwnetid)
from sis_provisioner.dao.uw_account import save_uw_account, set_bridge_id
from sis_provisioner.dao.pws import get_person
from sis_provisioner.account_managers import account_not_changed
from sis_provisioner.account_managers.loader import Loader


logger = logging.getLogger(__name__)


class GwsBridgeLoader(Loader):

    def __init__(self, worker, clogger=logger):
        super(GwsBridgeLoader, self).__init__(worker, clogger)

    def fetch_users(self):
        self.data_source = "GWS uw_members group"
        return list(self.gws_user_set)

    def process_users(self):
        """
        Process potential learners in GWS, add new users or update
        the exsiting users
        """
        for uwnetid in self.get_users_to_process():
            person = get_person(uwnetid)
            if person is None:
                self.logger.error(
                    "UWNetID '{0}' NOT in PWS, skip!".format(uwnetid))
                continue
            self.take_action(person)

    def take_action(self, person):
        """
        @param: person is a valid Person object
        """
        try:
            uw_account = save_uw_account(person)
            self.apply_change_to_bridge(uw_account, person)

        except Exception as ex:
            self.handle_exception("Save user {0} ".format(person.uwnetid),
                                  ex, traceback)

    def apply_change_to_bridge(self, uw_account, person):
        """
        @param: uw_account a valid UwAccount object to take action upon
        """
        exists, bridge_acc = self.match_bridge_account(uw_account)
        self.logger.debug("MATCH UW account {0} ==> Bridge account {1}".format(
            uw_account, bridge_acc))

        if exists is False:
            # account not exist in Bridge
            self.worker.add_new_user(uw_account, person)
            return

        if bridge_acc is None:
            # exists a deleted/terminated bridge account
            bridge_acc = self.worker.restore_user(uw_account)
            if bridge_acc is None:
                self.add_error("Failed to restore {0}\n".format(uw_account))
                return

        uw_account.set_bridge_id(bridge_acc.bridge_id)

        if not account_not_changed(uw_account, person, bridge_acc):
            # update the existing account with person data
            self.worker.update_user(bridge_acc, uw_account, person)

    def match_bridge_account(self, uw_account):
        """
        :return: a boolean value and an active BridgeUser object
        If exists an active account: True, a valid BridgeUser object
        If exist a terminated account: True, None
        If not exists: False, None
        """
        exi_prev = False
        prev_bri_acc = None
        if uw_account.has_prev_netid():
            exi_prev, prev_bri_acc = get_user_by_uwnetid(uw_account.prev_netid)

        exi_cur, cur_bri_acc = get_user_by_uwnetid(uw_account.netid)

        if exi_cur is False:
            # account of the current netid never existed
            return exi_prev, prev_bri_acc

        if exi_prev is False:
            # account of the previous netid never existed
            return exi_cur, cur_bri_acc

        if (prev_bri_acc is not None and cur_bri_acc is not None and
                prev_bri_acc.bridge_id != cur_bri_acc.bridge_id):
            # Found two active accounts, choose one to keep

            if self.del_bridge_account(prev_bri_acc):
                return True, cur_bri_acc

            if self.del_bridge_account(cur_bri_acc):
                return True, prev_bri_acc

            self.add_error("Please manually merge: {0} TO {1}".format(
                prev_bri_acc, cur_bri_acc))
            return True, cur_bri_acc

        # one active account and one deleted account
        if prev_bri_acc is not None:
            # account of the current netid is deleted
            return exi_prev, prev_bri_acc

        # account of the previous netid is deleted
        return exi_cur, cur_bri_acc

    def del_bridge_account(self, bridge_acc, conditional_del=True):
        """
        Return True if the desired deletion is carried out
        """
        if conditional_del is False or bridge_acc.no_learning_history():
            return self.worker.delete_user(bridge_acc)
        return False
