from restclients.exceptions import DataFailureException
from django.test import TestCase
from sis_provisioner.test import FPWS
from sis_provisioner.dao.pws import get_person, get_person_by_regid


class TestPwsDao(TestCase):

    def test_get_person(self):
        with self.settings(RESTCLIENTS_PWS_DAO_CLASS=FPWS):
            person = get_person('botgrad')
            self.assertIsNotNone(person)
            self.assertEqual(person.uwnetid, 'botgrad')
            self.assertEqual(person.uwregid,
                             "10000000000000000000000000000003")
            self.assertEqual(person.email1, "botgrad@uw.edu")
            self.assertEqual(person.home_department,
                             "OVP OF UW IT")

            self.assertRaises(DataFailureException,
                              get_person,
                              "supple")

    def test_get_person_by_regid(self):
        with self.settings(RESTCLIENTS_GWS_DAO_CLASS=FPWS):
            person = get_person_by_regid("10000000000000000000000000000005")
            self.assertIsNotNone(person)
            self.assertEqual(person.uwnetid, "faculty")
            self.assertEqual(person.uwregid,
                             "10000000000000000000000000000005")

            self.assertRaises(DataFailureException,
                              get_person_by_regid,
                              "00000000000000000000000000000000")
