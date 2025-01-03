# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging
import traceback
from uw_bridge.models import BridgeCustomField
from sis_provisioner.dao.uw_account import save_uw_account
from sis_provisioner.dao.pws import get_person
from sis_provisioner.models.work_positions import WORK_POSITION_FIELDS
from sis_provisioner.util.settings import (
    get_total_work_positions_to_load, get_group_member_add_window)
from sis_provisioner.account_managers import (
    get_email, get_job_title, get_first_name, get_full_name, get_surname,
    normalize_name, GET_POS_ATT_FUNCS, get_supervisor_bridge_id,
    get_custom_field_value, get_hired_date)
from sis_provisioner.account_managers.loader import Loader

logger = logging.getLogger(__name__)


class GwsBridgeLoader(Loader):

    """
    This class will load the new employees from gws.
    1. Add new user account to DB and Bridge
    2. Restore and update disabled/terminated account
    """

    def __init__(self, worker, clogger=logger):
        super(GwsBridgeLoader, self).__init__(worker, clogger)
        self.data_source = "Group new members"

    def fetch_users(self):
        return list(self.gws.get_added_members(get_group_member_add_window()))

    def get_bridge(self):
        return self.worker.bridge

    def process_users(self):
        """
        Process potential learners in GWS, add new users or update
        the exsiting users
        """
        for uwnetid in self.get_users_to_process():
            person = get_person(uwnetid)
            if self.is_invalid_person(uwnetid, person):
                continue
            self.total_checked_users += 1
            self.take_action(person)

    def take_action(self, person):
        """
        @param: person is a valid Person object
        """
        try:
            uw_account = save_uw_account(person)
            self.apply_change_to_bridge(uw_account, person)

        except Exception as ex:
            self.handle_exception(
                "Failed priority change on {0} ".format(person.uwnetid),
                ex, traceback)

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

        uw_account.set_ids(bridge_acc.bridge_id, person.employee_id)
        if (self.update_existing_accs() and
                not self.account_not_changed(bridge_acc, person, hrp_wkr)):
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
        first_name = normalize_name(get_first_name(person))
        return (person.uwnetid == bridge_acc.netid and
                get_email(person) == bridge_acc.email and
                get_full_name(person) == bridge_acc.full_name and
                first_name == bridge_acc.first_name and
                normalize_name(get_surname(person)) == bridge_acc.last_name and
                get_job_title(hrp_wkr) == bridge_acc.job_title and
                get_supervisor_bridge_id(hrp_wkr) == bridge_acc.manager_id and
                self.regid_not_changed(bridge_acc, person) and
                self.eid_not_changed(bridge_acc, person) and
                self.sid_not_changed(bridge_acc, person) and
                self.hired_date_not_changed(bridge_acc, hrp_wkr) and
                self.pos_data_not_changed(bridge_acc, hrp_wkr))

    def regid_not_changed(self, bridge_account, person):
        regid = get_custom_field_value(bridge_account,
                                       BridgeCustomField.REGID_NAME)
        return person.uwregid == regid

    def eid_not_changed(self, bridge_account, person):
        eid = get_custom_field_value(bridge_account,
                                     BridgeCustomField.EMPLOYEE_ID_NAME)
        return (person.employee_id is None and eid == '' or
                person.employee_id == eid)

    def sid_not_changed(self, bridge_account, person):
        sid = get_custom_field_value(bridge_account,
                                     BridgeCustomField.STUDENT_ID_NAME)
        return (person.student_number is None and sid == '' or
                person.student_number == sid)

    def pos_data_not_changed(self, bridge_account, hrp_wkr):
        for pos_num in range(get_total_work_positions_to_load()):
            pos_field_names = WORK_POSITION_FIELDS[pos_num]
            for i in range(len(pos_field_names)):
                bri_value = get_custom_field_value(bridge_account,
                                                   pos_field_names[i])
                hrp_value = GET_POS_ATT_FUNCS[i](hrp_wkr, pos_num)
                if (hrp_value is not None and hrp_value != bri_value or
                        hrp_value is None and bri_value != ''):
                    return False
        return True

    def hired_date_not_changed(self, bridge_account, hrp_wkr):
        hire_date = get_hired_date(hrp_wkr)
        hired_at = bridge_account.hired_at
        return (
            hire_date and hired_at and hired_at == hire_date or
            hire_date is None and hired_at is None)
