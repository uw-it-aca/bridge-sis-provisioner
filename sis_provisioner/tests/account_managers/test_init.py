from django.test import TransactionTestCase
from sis_provisioner.dao.pws import get_person, is_prior_netid
from sis_provisioner.account_managers import (
    account_not_changed, get_full_name, get_email,
    _not_changed_regid, _normalize_name, get_bridge_user_to_add,
    get_bridge_user_to_upd, save_bridge_id)
from sis_provisioner.tests import fdao_pws_override
from sis_provisioner.tests.account_managers import set_uw_account
from sis_provisioner.tests.dao import get_mock_bridge_user


@fdao_pws_override
class TestValidUser(TransactionTestCase):

    def test_account_not_changed(self):
        uw_account = set_uw_account('javerage')
        save_bridge_id(uw_account, 195)
        person = get_person('javerage')
        bridge_account = get_mock_bridge_user(
            195,
            "javerage",
            "javerage@uw.edu",
            "Average Joseph Student",
            "Average Joseph",
            "Student",
            "9136CCB8F66711D5BE060004AC494FFE")
        self.assertTrue(_not_changed_regid("9136CCB8F66711D5BE060004AC494FFE",
                                           bridge_account))
        self.assertTrue(
            account_not_changed(uw_account, person, bridge_account))

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
        self.assertEqual(_normalize_name("XXXXXXXXX Y AAAAAAAAA"),
                         "Xxxxxxxxx Y Aaaaaaaaa")
        self.assertEqual(_normalize_name(None), "")

    def test_get_bridge_user_to_add(self):
        person = get_person('javerage')
        buser = get_bridge_user_to_add(person)
        self.assertEqual(
            buser.json_data(),
            {'custom_fields': [{'custom_field_id': '5',
                                'value': '9136CCB8F66711D5BE060004AC494FFE'}],
             'email': 'javerage@uw.edu',
             'first_name': 'Average Joseph',
             'full_name': 'Average Joseph Student',
             'last_name': 'Student',
             'uid': 'javerage@uw.edu'})

    def test_get_bridge_user_to_upd(self):
        person = get_person('faculty')
        bridge_account = get_mock_bridge_user(
            198,
            "tyler",
            "tyler@uw.edu",
            "Tyler Faculty",
            "Tyler",
            "Faculty",
            "10000000000000000000000000000005")
        buser_acc = get_bridge_user_to_upd(person, bridge_account)
        self.assertEqual(
            buser_acc.json_data(),
            {'custom_fields': [],
             'email': 'faculty@uw.edu',
             'first_name': 'William E',
             'full_name': 'William E Faculty',
             'id': 198,
             'last_name': 'Faculty',
             'uid': 'faculty@uw.edu'})
