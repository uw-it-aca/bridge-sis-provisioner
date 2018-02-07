from django.test import TestCase
from restclients_core.exceptions import DataFailureException
from sis_provisioner.test import fdao_pws_override
from sis_provisioner.dao.pws import get_person, get_person_by_regid,\
    is_moved_netid, is_moved_regid


@fdao_pws_override
class TestPwsDao(TestCase):

    def test_get_person(self):
        person = get_person('botgrad')
        self.assertIsNotNone(person)
        self.assertEqual(person.uwnetid, 'botgrad')
        self.assertEqual(person.uwregid,
                         "10000000000000000000000000000003")
        self.assertEqual(person.email1, "botgrad@uw.edu")
        self.assertEqual(person.home_department,
                         "OVP OF UW IT")

    def test_get_person_by_regid(self):
        person = get_person_by_regid("10000000000000000000000000000005")
        self.assertIsNotNone(person)
        self.assertEqual(person.uwnetid, "faculty")
        self.assertEqual(person.uwregid,
                         "10000000000000000000000000000005")

        self.assertRaises(DataFailureException,
                          get_person_by_regid,
                          "00000000000000000000000000000000")

    def test_get_person_err404(self):
        self.assertRaises(DataFailureException,
                          get_person,
                          "supple")
        self.assertRaises(DataFailureException,
                          get_person,
                          'none')
        self.assertRaises(DataFailureException,
                          get_person,
                          'renamed')

    def test_is_moved_netid(self):
        self.assertTrue(is_moved_netid('changed'))
        self.assertFalse(is_moved_netid('javerage'))

    def test_is_moved_regid(self):
        self.assertTrue(is_moved_regid('0136CCB8F66711D5BE060004AC494FFE'))
        self.assertFalse(is_moved_regid('9136CCB8F66711D5BE060004AC494FFE'))
