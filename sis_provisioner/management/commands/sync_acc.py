# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging
import traceback
from django.core.management.base import BaseCommand
from uw_bridge.models import BridgeCustomField
from sis_provisioner.dao.hrp import get_worker
from sis_provisioner.dao.pws import get_person
from sis_provisioner.dao.uw_account import save_uw_account
from sis_provisioner.models.work_positions import WORK_POSITION_FIELDS
from sis_provisioner.account_managers.bridge_worker import BridgeWorker
from sis_provisioner.account_managers import (
    get_email, get_job_title, get_first_name, get_full_name, get_surname,
    normalize_name, GET_POS_ATT_FUNCS, get_supervisor_bridge_id,
    get_custom_field_value)


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Update an existing Bridge Account
    """
    def add_arguments(self, parser):
        parser.add_argument('uwnetid')

    def handle(self, *args, **options):
        uwnetid = options['uwnetid']
        try:
            person = get_person(uwnetid)
            logger.info("PWS data: {}\n\n".format(person))
            if person.is_test_entity:
                logger.error(
                    "{} IsTestEntity in PWS, skip!".format(uwnetid))
                return

            hrp_wkr = get_worker(person)
            logger.info("HRP data: {}\n\n".format(hrp_wkr))
            logger.info("Supervisor Bridge Id: {}\n\n".format(
                get_supervisor_bridge_id(hrp_wkr)))

            uw_acc = save_uw_account(person)
            logger.info("UW account in DB: {}\n\n".format(uw_acc))

            workr = BridgeWorker()
            bridge_acc = workr.bridge.get_user_by_uwnetid(uw_acc.netid)
            logger.info("Bridge account: {}\n\n".format(bridge_acc))

            if self.account_not_changed(bridge_acc, person, hrp_wkr):
                # update the existing account with person data
                logger.info("Account Not Changed!\n")
                return
            workr.update_user(bridge_acc, uw_acc, person, hrp_wkr)

        except Exception as ex:
            logger.error(ex)
            logger.error(traceback.format_exc(chain=False))

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
                self.pos_data_not_changed(bridge_acc, hrp_wkr)
                )

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
        for pos_num in range(2):
            pos_field_names = WORK_POSITION_FIELDS[pos_num]
            for i in range(len(pos_field_names)):
                bri_value = get_custom_field_value(bridge_account,
                                                   pos_field_names[i])
                hrp_value = GET_POS_ATT_FUNCS[i](hrp_wkr, pos_num)
                if (hrp_value is not None and hrp_value != bri_value or
                        hrp_value is None and bri_value != ''):
                    return False
        return True
