"""
This class will load all the users in gws uw_member, uw_afiliate groups.
Check against PWS Person, apply high priority changes.
1. Add new user account (to DB and Bridge)
2. Restore and update disabled/terminated account
3. Update account if uwnetid has changed
"""

import logging
import traceback
from uw_bridge.models import BridgeUser
from sis_provisioner.dao.hrp import get_worker
from sis_provisioner.dao.uw_account import save_uw_account, set_bridge_id
from sis_provisioner.dao.pws import get_person
from sis_provisioner.account_managers import (
    get_full_name, get_email, get_job_title, normalize_name,
    get_pos1_budget_code, get_pos1_job_code, get_job_title,
    get_pos1_job_class, get_pos1_org_code, get_pos1_org_name)
from sis_provisioner.account_managers.loader import Loader


logger = logging.getLogger(__name__)


class GwsBridgeLoader(Loader):

    def __init__(self, worker, clogger=logger):
        super(GwsBridgeLoader, self).__init__(worker, clogger)

    def fetch_users(self):
        self.data_source = "GWS uw_members group"
        return list(self.gws_user_set)

    def get_bridge(self):
        return self.worker.bridge

    def get_hrp_worker(self, person):
        return get_worker(person)

    def process_users(self):
        """
        Process potential learners in GWS, add new users or update
        the exsiting users
        """
        for uwnetid in self.get_users_to_process():
            person = get_person(uwnetid)
            if person is None:
                self.logger.error(
                    "{0} NOT in PWS, skip!".format(uwnetid))
                continue
            self.take_action(person)

    def take_action(self, person, priority_changes_only=True):
        """
        @param: person is a valid Person object
        """
        try:
            uw_account = save_uw_account(person)
            if (priority_changes_only and
                    not self.is_priority_change(uw_account)):
                return
            self.apply_change_to_bridge(uw_account, person)

        except Exception as ex:
            self.handle_exception(
                "Failed priority change on {0} ".format(person.uwnetid),
                ex, traceback)

    def is_priority_change(self, uw_account):
        """
        Given the user appears in GWS groups now
        """
        return (uw_account.last_updated is None or
                uw_account.netid_changed() or
                uw_account.disabled or
                uw_account.has_terminate_date())

    def apply_change_to_bridge(self, uw_account, person):
        """
        @param: uw_account a valid UwAccount object to take action upon
        """
        hrp_wkr = self.get_hrp_worker(person)

        bridge_acc = self.match_bridge_account(uw_account)
        self.logger.debug("MATCH UW account {0} ==> Bridge account {1}".format(
            uw_account, bridge_acc))

        if bridge_acc is None:
            if uw_account.disabled:
                # exists a deleted bridge account
                bridge_acc = self.worker.restore_user(uw_account)
                if bridge_acc is None:
                    self.add_error("Failed to restore {0}".format(uw_account))
                    return
            else:
                # account not exist in Bridge
                self.worker.add_new_user(uw_account, person, hrp_wkr)
                return

        uw_account.set_bridge_id(bridge_acc.bridge_id)
        if not self.account_not_changed(bridge_acc, person, hrp_wkr):
            # update the existing account with person data
            self.worker.update_user(bridge_acc, uw_account,
                                    person, hrp_wkr)

    def match_bridge_account(self, uw_account):
        """
        :return: a BridgeUser object or None
        """
        prev_bri_acc = None
        if uw_account.has_prev_netid():
            prev_bri_acc = self.get_bridge().get_user_by_uwnetid(
                uw_account.prev_netid)

        cur_bri_acc = self.get_bridge().get_user_by_uwnetid(uw_account.netid)

        if cur_bri_acc is None:
            return prev_bri_acc

        if prev_bri_acc is None:
            return cur_bri_acc

        if prev_bri_acc.bridge_id != cur_bri_acc.bridge_id:
            # Found two active accounts, choose one to keep

            if self.del_bridge_account(prev_bri_acc):
                return cur_bri_acc

            if self.del_bridge_account(cur_bri_acc):
                return prev_bri_acc

            self.add_error("Please manually merge: {0} TO {1}".format(
                prev_bri_acc, cur_bri_acc))
            return cur_bri_acc

    def del_bridge_account(self, bridge_acc, conditional_del=True):
        """
        Return True if the desired deletion is carried out
        """
        if conditional_del is False or bridge_acc.no_learning_history():
            return self.worker.delete_user(bridge_acc)
        return False

    def account_not_changed(self, bridge_acc, person, hrp_wkr):
        """
        :param bridge_acc: a valid BridgeUser object
        :param person: a valid Person object
        :param hrp_wkr: a valid Worker object
        :return: True if the attributes have the same values
        """
        return (
            person.uwnetid == bridge_acc.netid and
            get_email(person) == bridge_acc.email and
            get_full_name(person) == bridge_acc.full_name and
            normalize_name(person.surname) == bridge_acc.last_name and
            get_job_title(hrp_wkr) == bridge_acc.job_title and
            self.worker.regid_not_changed(bridge_acc, person) and
            self.worker.eid_not_changed(bridge_acc, person) and
            self.worker.sid_not_changed(bridge_acc, person) and
            self.worker.pos1_budget_code_not_changed(bridge_acc, hrp_wkr) and
            self.worker.pos1_job_code_not_changed(bridge_acc, hrp_wkr) and
            self.worker.pos1_job_class_not_changed(bridge_acc, hrp_wkr) and
            self.worker.pos1_org_code_not_changed(bridge_acc, hrp_wkr) and
            self.worker.pos1_org_name_not_changed(bridge_acc, hrp_wkr))
