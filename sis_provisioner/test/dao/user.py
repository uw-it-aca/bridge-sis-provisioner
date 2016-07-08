from restclients.exceptions import DataFailureException
from django.test import TestCase
from sis_provisioner.test import FPWS
from sis_provisioner.dao.user import create_user, get_user_from_db


class TestUserDao(TestCase):

    def test_create_user(self):
        with self.settings(RESTCLIENTS_PWS_DAO_CLASS=FPWS):
            user = create_user('staff')
            self.assertIsNotNone(user)
            self.assertEqual(user.netid, 'staff')

    def test_err_case(self):
        with self.settings(RESTCLIENTS_GWS_DAO_CLASS=FPWS):
            self.assertRaises(DataFailureException,
                              create_user,
                              "supple")
            self.assertIsNone(get_user_from_db("none"))
