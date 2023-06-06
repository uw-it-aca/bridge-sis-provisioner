# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TransactionTestCase
from uw_bridge.models import BridgeCustomField, BridgeUser
from uw_hrp.models import Person
from sis_provisioner.dao.pws import get_person
from sis_provisioner.dao.hrp import get_worker
from sis_provisioner.account_managers import (
    get_first_name, get_full_name, get_surname,
    get_email, normalize_name, get_job_title, get_work_position,
    GET_POS_ATT_FUNCS, get_custom_field_value, get_supervisor_bridge_id)
from sis_provisioner.tests.account_managers import (
    new_custom_field, set_db_records)


def get_hrp_wkr(testid):
    person = get_person('javerage')
    return get_worker(person)


class TestValidUser(TransactionTestCase):

    def test_get_first_name(self):
        person = get_person('javerage')
        self.assertEqual(get_first_name(person), "Average")

        person.preferred_first_name = ""
        self.assertEqual(get_first_name(person), "Average Joseph")

    def test_get_full_name(self):
        person = get_person('javerage')
        self.assertEqual(get_full_name(person), "Average Joseph Student")

        person.display_name = ""
        self.assertEqual(get_full_name(person), "Average Student")

    def test_get_surname(self):
        person = get_person('javerage')
        self.assertEqual(get_surname(person), "Student")

        person.preferred_surname = ""
        self.assertEqual(get_surname(person), "Student")

    def test_get_email(self):
        person = get_person('staff')
        self.assertEqual(get_email(person), "staff@uw.edu")

        person = get_person('retiree')
        self.assertEqual(get_email(person), "retiree@uw.edu")

        person.email_addresses.append("ellen@uw.edu. ")
        self.assertEqual(get_email(person), "ellen@uw.edu")

    def test_normalize_name(self):
        self.assertEqual(normalize_name("XXXXXXXXX Y AAAAAAAAA"),
                         "Xxxxxxxxx Y Aaaaaaaaa")
        self.assertEqual(normalize_name(None), "")

    def test_get_custom_field_value(self):
        bridge_acc = BridgeUser(netid='javerage')
        self.assertEqual(get_custom_field_value(
            bridge_acc, BridgeCustomField.REGID_NAME), "")
        bridge_acc.custom_fields[BridgeCustomField.REGID_NAME] = \
            new_custom_field(BridgeCustomField.REGID_NAME, "1")
        self.assertEqual(get_custom_field_value(
            bridge_acc, BridgeCustomField.STUDENT_ID_NAME), "")
        self.assertEqual(get_custom_field_value(
            bridge_acc, BridgeCustomField.REGID_NAME), "1")

    def test_get_work_position(self):
        self.assertIsNone(get_work_position(None, -1))
        hrp_wkr = get_hrp_wkr('javerage')
        self.assertIsNone(get_work_position(hrp_wkr, -1))

        pos1 = get_work_position(hrp_wkr, 0)
        self.assertTrue(pos1.is_primary)
        self.assertEqual(pos1.job_title, "Student Assistant (NE H)")

        hrp_wkr.worker_details[0].primary_position = None
        self.assertIsNone(get_work_position(hrp_wkr, 0))

        pos2 = get_work_position(hrp_wkr, 1)
        self.assertFalse(pos2.is_primary)
        self.assertEqual(
            pos2.job_title, "UW Press Marketing & Sales Student Associate")

        self.assertIsNone(get_work_position(hrp_wkr, 3))

        hrp_wkr.worker_details[0].other_active_positions = []
        self.assertIsNone(get_work_position(hrp_wkr, 1))

    def test_get_job_title(self):
        self.assertIsNone(get_job_title(None))
        hrp_wkr = get_hrp_wkr('javerage')
        self.assertEqual(get_job_title(hrp_wkr),
                         "Student Assistant (NE H)")
        hrp_wkr.worker_details[0].primary_position = None
        self.assertIsNone(get_job_title(hrp_wkr))

    def test_get_pos_budget_code(self):
        func_name = GET_POS_ATT_FUNCS[0]
        self.assertIsNone(func_name(None, 0))
        hrp_wkr = get_hrp_wkr('javerage')
        self.assertEqual(func_name(hrp_wkr, 0),
                         "060418 CHEMISTRY")
        hrp_wkr.worker_details[0].primary_position = None
        self.assertIsNone(func_name(hrp_wkr, 0))

        self.assertEqual(func_name(hrp_wkr, 1),
                         "141614 UNIVERSITY PRESS")

    def test_get_pos_job_class(self):
        func_name = GET_POS_ATT_FUNCS[1]
        self.assertIsNone(func_name(None, 0))
        hrp_wkr = get_hrp_wkr('javerage')
        self.assertEqual(func_name(hrp_wkr, 0),
                         "Undergraduate Student")
        hrp_wkr.worker_details[0].primary_position = None
        self.assertIsNone(func_name(hrp_wkr, 0))

        self.assertEqual(func_name(hrp_wkr, 1),
                         "Undergraduate Student")

    def test_get_pos_job_code(self):
        func_name = GET_POS_ATT_FUNCS[2]
        self.assertIsNone(func_name(None, 0))
        hrp_wkr = get_hrp_wkr('javerage')
        self.assertEqual(func_name(hrp_wkr, 0), "10804")
        hrp_wkr.worker_details[0].primary_position.job_profile = None
        self.assertIsNone(func_name(hrp_wkr, 0))

        self.assertEqual(func_name(hrp_wkr, 1), "10889")

    def test_get_pos_location(self):
        func_name = GET_POS_ATT_FUNCS[3]
        self.assertIsNone(func_name(None, 0))
        hrp_wkr = get_hrp_wkr('javerage')
        self.assertEqual(func_name(hrp_wkr, 0), "Seattle Campus")
        hrp_wkr.worker_details[0].primary_position = None
        self.assertIsNone(func_name(hrp_wkr, 0))

        self.assertEqual(func_name(hrp_wkr, 1), "Seattle, Non-Campus")

    def test_get_pos_org_code(self):
        func_name = GET_POS_ATT_FUNCS[4]
        self.assertIsNone(func_name(None, 0))
        hrp_wkr = get_hrp_wkr('javerage')
        self.assertEqual(func_name(hrp_wkr, 0),
                         "CAS")
        hrp_wkr.worker_details[0].primary_position = None
        self.assertIsNone(func_name(hrp_wkr, 0))

        self.assertEqual(func_name(hrp_wkr, 1),
                         "LIB")

    def test_get_pos_org_name(self):
        func_name = GET_POS_ATT_FUNCS[5]
        self.assertIsNone(func_name(None, 0))
        hrp_wkr = get_hrp_wkr('javerage')
        self.assertEqual(func_name(hrp_wkr, 0),
                         "Chemistry: Theberge JM Student")
        hrp_wkr.worker_details[0].primary_position = None
        self.assertIsNone(func_name(hrp_wkr, 0))

        self.assertEqual(func_name(hrp_wkr, 1),
                         "UW Press: Marketing & Sales JM Student")

    def test_get_pos_unit_code(self):
        func_name = GET_POS_ATT_FUNCS[6]
        self.assertIsNone(func_name(None, 0))
        hrp_wkr = get_hrp_wkr('javerage')
        self.assertEqual(func_name(hrp_wkr, 0), "")
        hrp_wkr.worker_details[0].primary_position = None
        self.assertIsNone(func_name(hrp_wkr, 0))

        self.assertEqual(func_name(hrp_wkr, 1), "")

    def test_get_supervisor_bridge_id(self):
        set_db_records()
        hrp_wkr = get_hrp_wkr('javerage')
        self.assertEqual(get_supervisor_bridge_id(hrp_wkr), 196)

        # hrp_wkr is None
        self.assertEqual(get_supervisor_bridge_id(None), 0)

        # manager employee_id is None
        hrp_wkr = Person(netid="x",
                         regid="111",
                         employee_id="1")
        self.assertEqual(get_supervisor_bridge_id(hrp_wkr), 0)

        # manager employee_id is the same as the employee's
        hrp_wkr = Person(netid="x",
                         regid="111",
                         employee_id="1",
                         primary_manager_id="1")
        self.assertEqual(get_supervisor_bridge_id(hrp_wkr), 0)

        # manager employee_id not in local DB
        hrp_wkr = Person(netid="javerage",
                         regid="111111111111111111111111111111",
                         employee_id="1",
                         primary_manager_id="11")
        self.assertEqual(get_supervisor_bridge_id(hrp_wkr), 0)

        # manager's uw account is the same the user's
        hrp_wkr = Person(netid="javerage",
                         regid="111111111111111111111111111111",
                         employee_id="1",
                         primary_manager_id="123456789")
        self.assertEqual(get_supervisor_bridge_id(hrp_wkr), 0)
