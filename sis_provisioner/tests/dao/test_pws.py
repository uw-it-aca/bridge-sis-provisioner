from django.test import TestCase
from sis_provisioner.dao.pws import (
    get_person, is_prior_netid, is_active_worker)
from sis_provisioner.tests import fdao_pws_override


@fdao_pws_override
class TestPwsDao(TestCase):

    def test_get_person(self):
        person = get_person("faculty")
        self.assertIsNotNone(person)
        self.assertEqual(person.uwnetid, 'faculty')
        self.assertEqual(person.uwregid,
                         "10000000000000000000000000000005")
        self.assertEqual(person.email_addresses[0],
                         "faculty@uw.edu")
        self.assertEqual(len(person.prior_uwnetids), 1)
        self.assertEqual(len(person.prior_uwregids), 1)
        self.assertEqual(person.prior_uwnetids[0], "tyler")
        self.assertEqual(person.prior_uwregids[0],
                         "10000000000000000000000000000000")
        self.assertEqual(person.display_name, "William E Faculty")
        self.assertEqual(person.preferred_first_name, "William E")
        self.assertEqual(person.preferred_surname, "Faculty")
        self.assertEqual(person.employee_id, "000000005")

        self.assertIsNone(get_person("not_in_pws"))
        self.assertIsNone(get_person("0 in valid uw netid"))

    def test_is_prior_netid(self):
        person = get_person("faculty")
        self.assertTrue(is_prior_netid("tyler", person))

    def test_is_active_worker(self):
        person = get_person("faculty")
        self.assertTrue(is_active_worker(person))
        person = get_person("ellen")
        self.assertTrue(is_active_worker(person))
        person = get_person("retiree")
        self.assertTrue(is_active_worker(person))

        person = get_person("leftuw")
        self.assertFalse(is_active_worker(person))
        person = get_person("alumni")
        self.assertFalse(is_active_worker(person))
