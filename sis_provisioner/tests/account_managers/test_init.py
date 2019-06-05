from django.test import TransactionTestCase
from sis_provisioner.dao.pws import get_person
from sis_provisioner.account_managers import (
    get_full_name, get_email, normalize_name, get_regid)
from sis_provisioner.tests.dao import get_mock_bridge_user


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

    def test_get_regid(self):
        bridge_acc = get_mock_bridge_user(
            198,
            "tyler",
            "tyler@uw.edu",
            "Tyler Faculty",
            "Tyler",
            "Faculty",
            "10000000000000000000000000000005")
        self.assertEqual(get_regid(bridge_acc),
                         "10000000000000000000000000000005")

        bridge_acc.custom_fields = {}
        self.assertIsNone(get_regid(bridge_acc))
