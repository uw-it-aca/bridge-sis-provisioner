# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
The BridgeWorker class will apply actions on the user account in Bridge
via the Bridge APIs.
"""

import logging
import traceback
from uw_bridge.models import BridgeUser, BridgeCustomField
from sis_provisioner.dao.bridge import BridgeUsers
from sis_provisioner.models.work_positions import WORK_POSITION_FIELDS
from sis_provisioner.util.settings import get_total_work_positions_to_load
from sis_provisioner.account_managers import (
    get_email, get_first_name, get_full_name, get_surname, normalize_name,
    get_job_title, GET_POS_ATT_FUNCS, get_supervisor_bridge_id, get_hired_date)
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
        self.total_work_positions = get_total_work_positions_to_load()

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

    def _uid_matched(self, uw_account, ret_bridge_user):
        return (ret_bridge_user is not None and
                ret_bridge_user.netid == uw_account.netid)

    def add_new_user(self, uw_account, person, hrp_wkr):
        action = "CREATE in Bridge: {0}".format(uw_account.netid)
        try:
            bri_acc = self.get_bridge_user_to_add(person, hrp_wkr)
            bridge_account = self.bridge.add_user(bri_acc)
            if self._uid_matched(uw_account, bridge_account):
                uw_account.set_ids(bridge_account.bridge_id,
                                   person.employee_id)
                self.total_new_users_count += 1
                logger.info("{0} ==> {1}".format(
                    action, bri_acc.to_json_post()))
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
                logger.info("{0} ==> {1}".format(action, bridge_account))
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
            logger.info("{0} ==> {1}".format(action, bridge_account))
            return
        self.append_error("Unmatched UID {0}\n".format(action))

    def update_user(self, bridge_account, uw_account, person, hrp_wkr):
        self.set_bridge_user_to_update(person, hrp_wkr, bridge_account)
        action = "UPDATE in Bridge: {}".format(bridge_account)
        try:
            if uw_account.netid_changed():
                self.update_uid(uw_account)

            ret_bri_acc = self.bridge.update_user(bridge_account)
            if self._uid_matched(uw_account, ret_bri_acc):
                uw_account.set_updated()
                self.total_updated_count += 1
                logger.debug("{0} ==> {1}".format(
                    action, bridge_account.to_json_patch()))
                return
            self.append_error("Unmatched UID {0}\n".format(action))
        except Exception as ex:
            self.handle_exception(action, ex, traceback)

    def get_bridge_user_to_add(self, person, hrp_wkr):
        """
        :param person: a valid Person object
        :return: a BridgeUser object
        """
        user = BridgeUser(
            netid=person.uwnetid,
            email=get_email(person),
            full_name=get_full_name(person),
            first_name=normalize_name(get_first_name(person)),
            last_name=normalize_name(get_surname(person)),
            job_title=get_job_title(hrp_wkr),
            hired_at=get_hired_date(hrp_wkr),
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

        for pos_num in range(self.total_work_positions):
            pos_field_names = WORK_POSITION_FIELDS[pos_num]
            for i in range(len(pos_field_names)):
                self.add_custom_field(user,
                                      pos_field_names[i],
                                      GET_POS_ATT_FUNCS[i](hrp_wkr, pos_num))
        return user

    def add_custom_field(self, bridge_account, field_name, value):
        bridge_account.custom_fields[field_name] = \
            self.bridge.custom_fields.new_custom_field(field_name, value)

    def set_bridge_user_to_update(self, person, hrp_wkr, bridge_account):
        """
        :param person: a valid Person object
        :param hrp_wkr: a valid Worker object
        :param bridge_account: a BridgeUser object to be updated
        """
        bridge_account.netid = person.uwnetid
        bridge_account.email = get_email(person)
        bridge_account.full_name = get_full_name(person)
        bridge_account.first_name = normalize_name(get_first_name(person))
        bridge_account.last_name = normalize_name(get_surname(person))
        bridge_account.job_title = get_job_title(hrp_wkr)
        bridge_account.hired_at = get_hired_date(hrp_wkr)
        bridge_account.manager_id = get_supervisor_bridge_id(hrp_wkr)

        self.update_custom_field(bridge_account,
                                 BridgeCustomField.REGID_NAME,
                                 person.uwregid)
        self.update_custom_field(bridge_account,
                                 BridgeCustomField.EMPLOYEE_ID_NAME,
                                 person.employee_id)
        self.update_custom_field(bridge_account,
                                 BridgeCustomField.STUDENT_ID_NAME,
                                 person.student_number)
        for pos_num in range(self.total_work_positions):
            pos_field_names = WORK_POSITION_FIELDS[pos_num]
            for i in range(len(pos_field_names)):
                self.update_custom_field(bridge_account,
                                         pos_field_names[i],
                                         GET_POS_ATT_FUNCS[i](hrp_wkr,
                                                              pos_num))
        return bridge_account

    def update_custom_field(self, bridge_account, field_name, value):
        cf = bridge_account.get_custom_field(field_name)
        if cf is None:
            self.add_custom_field(bridge_account, field_name, value)
        else:
            cf.value = value

    def update_user_role(self, bridge_account):
        action = "UPDATE {0}'s roles".format(bridge_account.netid)
        try:
            ret_bri_acc = self.bridge.update_user_roles(bridge_account)
            if ret_bri_acc is not None:
                self.total_updated_count += 1
                logger.info("{0} ==> {1}".format(
                    action, ret_bri_acc.roles_to_json()))
                return
        except Exception as ex:
            self.handle_exception(action, ex, traceback)
