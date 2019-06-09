"""
The BridgeWorker class will apply actions on the user account in Bridge
via the Bridge APIs.
"""

import logging
import traceback
from uw_bridge.models import BridgeUser, BridgeCustomField
from sis_provisioner.dao.bridge import BridgeUsers
from sis_provisioner.account_managers import (
    get_email, get_full_name, normalize_name, get_custom_field_value,
    get_pos1_budget_code, get_pos1_job_code, get_job_title,
    get_pos1_job_class, get_pos1_org_code, get_pos1_org_name,
    get_supervisor_bridge_id)
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

    def add_new_user(self, uw_account, person, hrp_wkr):
        action = "CREATE in Bridge: {0}".format(uw_account.netid)
        try:
            bridge_account = self.bridge.add_user(
                self.get_bridge_user_to_add(person, hrp_wkr))

            if self._uid_matched(uw_account, bridge_account):
                uw_account.set_ids(bridge_account.bridge_id,
                                   person.employee_id)
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

    def update_user(self, bridge_account, uw_account, person, hrp_wkr):
        user_data = self.get_bridge_user_to_upd(
            person, hrp_wkr, bridge_account)
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

    def get_bridge_user_to_add(self, person, hrp_wkr):
        """
        :param person: a valid Person object
        :return: a BridgeUser object
        """
        user = BridgeUser(netid=person.uwnetid,
                          email=get_email(person),
                          full_name=get_full_name(person),
                          first_name=normalize_name(person.first_name),
                          last_name=normalize_name(person.surname),
                          job_title=get_job_title(hrp_wkr),
                          manager_id=get_supervisor_bridge_id(hrp_wkr))
        self.add_custom_field(user,
                              BridgeCustomField.REGID_NAME,
                              person.uwregid)
        if person.employee_id is not None:
            self.add_custom_field(user,
                                  BridgeCustomField.EMPLOYEE_ID_NAME,
                                  person.employee_id)
        if person.student_number is not None:
            self.add_custom_field(user,
                                  BridgeCustomField.STUDENT_ID_NAME,
                                  person.student_number)

        if (hrp_wkr is not None and
                hrp_wkr.primary_position is not None):
            self.add_custom_field(user,
                                  BridgeCustomField.POS1_BUDGET_CODE,
                                  get_pos1_budget_code(hrp_wkr))
            self.add_custom_field(user,
                                  BridgeCustomField.POS1_JOB_CODE,
                                  get_pos1_job_code(hrp_wkr))
            self.add_custom_field(user,
                                  BridgeCustomField.POS1_JOB_CLAS,
                                  get_pos1_job_class(hrp_wkr))
            self.add_custom_field(user,
                                  BridgeCustomField.POS1_ORG_CODE,
                                  get_pos1_org_code(hrp_wkr))
            self.add_custom_field(user,
                                  BridgeCustomField.POS1_ORG_NAME,
                                  get_pos1_org_name(hrp_wkr))
        return user

    def get_bridge_user_to_upd(self, person, hrp_wkr, bridge_account):
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
            last_name=normalize_name(person.surname),
            job_title=get_job_title(hrp_wkr),
            manager_id=get_supervisor_bridge_id(hrp_wkr))

        if not self.regid_not_changed(bridge_account, person):
            self.add_custom_field(user,
                                  BridgeCustomField.REGID_NAME,
                                  person.uwregid)

        if not self.eid_not_changed(bridge_account, person):
            self.add_custom_field(user,
                                  BridgeCustomField.EMPLOYEE_ID_NAME,
                                  person.employee_id)

        if not self.sid_not_changed(bridge_account, person):
            self.add_custom_field(user,
                                  BridgeCustomField.STUDENT_ID_NAME,
                                  person.student_number)

        if not self.pos1_budget_code_not_changed(bridge_account, hrp_wkr):
            self.add_custom_field(user,
                                  BridgeCustomField.POS1_BUDGET_CODE,
                                  get_pos1_budget_code(hrp_wkr))

        if not self.pos1_job_code_not_changed(bridge_account, hrp_wkr):
            self.add_custom_field(user,
                                  BridgeCustomField.POS1_JOB_CODE,
                                  get_pos1_job_code(hrp_wkr))

        if not self.pos1_job_class_not_changed(bridge_account, hrp_wkr):
            self.add_custom_field(user,
                                  BridgeCustomField.POS1_JOB_CLAS,
                                  get_pos1_job_class(hrp_wkr))

        if not self.pos1_org_code_not_changed(bridge_account, hrp_wkr):
            self.add_custom_field(user,
                                  BridgeCustomField.POS1_ORG_CODE,
                                  get_pos1_org_code(hrp_wkr))

        if not self.pos1_org_name_not_changed(bridge_account, hrp_wkr):
            self.add_custom_field(user,
                                  BridgeCustomField.POS1_ORG_NAME,
                                  get_pos1_org_name(hrp_wkr))
        return user

    def add_custom_field(self, user, field_name, value):
        user.custom_fields[field_name] = \
            self.bridge.custom_fields.new_custom_field(field_name, value)

    def regid_not_changed(self, bridge_account, person):
        regid = get_custom_field_value(bridge_account,
                                       BridgeCustomField.REGID_NAME)
        return regid is not None and regid == person.uwregid

    def eid_not_changed(self, bridge_account, person):
        eid = get_custom_field_value(bridge_account,
                                     BridgeCustomField.EMPLOYEE_ID_NAME)
        return (person.employee_id is None and eid is None or
                eid == person.employee_id)

    def sid_not_changed(self, bridge_account, person):
        sid = get_custom_field_value(bridge_account,
                                     BridgeCustomField.STUDENT_ID_NAME)
        return (person.student_number is None and sid is None or
                sid == person.student_number)

    def pos1_budget_code_not_changed(self, bridge_account, hrp_wkr):
        cur_pos1_budget_code = get_custom_field_value(
            bridge_account, BridgeCustomField.POS1_BUDGET_CODE)
        hrp_pos1_budget_code = get_pos1_budget_code(hrp_wkr)
        return (cur_pos1_budget_code is None and
                hrp_pos1_budget_code is None or
                cur_pos1_budget_code == hrp_pos1_budget_code)

    def pos1_job_code_not_changed(self, bridge_account, hrp_wkr):
        cur_pos1_job_code = get_custom_field_value(
            bridge_account, BridgeCustomField.POS1_JOB_CODE)
        hrp_pos1_job_code = get_pos1_job_code(hrp_wkr)
        return (cur_pos1_job_code is None and hrp_pos1_job_code is None or
                cur_pos1_job_code == hrp_pos1_job_code)

    def pos1_job_class_not_changed(self, bridge_account, hrp_wkr):
        cur_pos1_job_class = get_custom_field_value(
            bridge_account, BridgeCustomField.POS1_JOB_CLAS)
        hrp_pos1_job_class = get_pos1_job_class(hrp_wkr)
        return (cur_pos1_job_class is None and hrp_pos1_job_class is None or
                cur_pos1_job_class == hrp_pos1_job_class)

    def pos1_org_code_not_changed(self, bridge_account, hrp_wkr):
        cur_pos1_org_code = get_custom_field_value(
            bridge_account, BridgeCustomField.POS1_ORG_CODE)
        hrp_pos1_org_code = get_pos1_org_code(hrp_wkr)
        return (cur_pos1_org_code is None and hrp_pos1_org_code is None or
                cur_pos1_org_code == hrp_pos1_org_code)

    def pos1_org_name_not_changed(self, bridge_account, hrp_wkr):
        cur_pos1_org_name = get_custom_field_value(
            bridge_account, BridgeCustomField.POS1_ORG_NAME)
        hrp_pos1_org_name = get_pos1_org_name(hrp_wkr)
        return (cur_pos1_org_name is None and hrp_pos1_org_name is None or
                cur_pos1_org_name == hrp_pos1_org_name)
