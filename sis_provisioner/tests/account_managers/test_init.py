from django.test import TransactionTestCase
from uw_bridge.models import BridgeCustomField, BridgeUser
from sis_provisioner.dao.pws import get_person
from sis_provisioner.dao.hrp import get_worker
from sis_provisioner.account_managers import (
    get_full_name, get_email, normalize_name, get_job_title,
    get_pos1_budget_code, get_pos1_job_code, get_job_title,
    get_pos1_job_class, get_pos1_org_code, get_pos1_org_name,
    get_custom_field_value)
from sis_provisioner.tests.account_managers import new_custom_field


class TestValidUser(TransactionTestCase):

    def test_get_full_name(self):
        person = get_person('javerage')
        self.assertEqual(get_full_name(person), "Average Joseph Student")

        person.display_name = ""
        self.assertEqual(get_full_name(person), "Average Student")

    def test_get_email(self):
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
        self.assertIsNone(get_custom_field_value(
            bridge_acc, BridgeCustomField.REGID_NAME))
        bridge_acc.custom_fields[BridgeCustomField.REGID_NAME] = \
            new_custom_field(BridgeCustomField.REGID_NAME, "1")
        self.assertIsNone(get_custom_field_value(
            bridge_acc, BridgeCustomField.STUDENT_ID_NAME))
        self.assertEqual(get_custom_field_value(
            bridge_acc, BridgeCustomField.REGID_NAME), "1")

    def test_get_job_title(self):
        self.assertIsNone(get_job_title(None))
        person = get_person('javerage')
        hrp_wkr = get_worker(person)
        self.assertEqual(get_job_title(hrp_wkr),
                         "Student Reference Specialist - GMM")
        hrp_wkr.primary_position = None
        self.assertIsNone(get_job_title(hrp_wkr))

    def test_get_pos1_job_class(self):
        self.assertIsNone(get_pos1_job_class(None))
        person = get_person('javerage')
        hrp_wkr = get_worker(person)
        self.assertEqual(get_pos1_job_class(hrp_wkr),
                         "Undergraduate Student")
        hrp_wkr.primary_position = None
        self.assertIsNone(get_pos1_job_class(hrp_wkr))

    def test_get_pos1_job_code(self):
        self.assertIsNone(get_pos1_job_code(None))
        person = get_person('javerage')
        hrp_wkr = get_worker(person)
        self.assertEqual(get_pos1_job_code(hrp_wkr),
                         "10875")
        hrp_wkr.primary_position = None
        self.assertIsNone(get_pos1_job_code(hrp_wkr))

    def test_get_pos1_budget_code(self):
        self.assertIsNone(get_pos1_budget_code(None))
        person = get_person('javerage')
        hrp_wkr = get_worker(person)
        self.assertEqual(get_pos1_budget_code(hrp_wkr),
                         "2070001000")
        hrp_wkr.primary_position = None
        self.assertIsNone(get_pos1_budget_code(hrp_wkr))

    def test_get_pos1_org_code(self):
        self.assertIsNone(get_pos1_org_code(None))
        person = get_person('javerage')
        hrp_wkr = get_worker(person)
        self.assertEqual(get_pos1_org_code(hrp_wkr),
                         "LIB:")
        hrp_wkr.primary_position = None
        self.assertIsNone(get_pos1_org_code(hrp_wkr))

    def test_get_pos1_org_name(self):
        self.assertIsNone(get_pos1_org_name(None))
        person = get_person('javerage')
        hrp_wkr = get_worker(person)
        self.assertEqual(get_pos1_org_name(hrp_wkr),
                         "GMMN: Public Services JM Student")
        hrp_wkr.primary_position = None
        self.assertIsNone(get_pos1_org_name(hrp_wkr))
