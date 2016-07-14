from django.conf import settings
from django.test import TransactionTestCase
from django.test.utils import override_settings
from sis_provisioner.test import FPWS
from sis_provisioner.csv.user_formatter import get_headers, get_attr_list
from sis_provisioner.dao.user import create_user


class TestUserFormatter(TransactionTestCase):

    def test_get_headers(self):
        self.assertEqual(','.join(get_headers()),
                         ("Unique ID,Regid,Name,Email," +
                          "employee_department,student_department," +
                          "alumni,employee,faculty,staff,student"))

    def test_get_attr_list(self):
        with self.settings(RESTCLIENTS_PWS_DAO_CLASS=FPWS):

            user = create_user('staff')
            user_attr_list = get_attr_list(user)

            self.assertEqual(len(user_attr_list), 11)
            self.assertEqual(user_attr_list[0],
                             "staff@washington.edu")
            self.assertEqual(user_attr_list[1],
                             "10000000000000000000000000000001")
            self.assertEqual(user_attr_list[2],
                             "Staff, James Average")
            self.assertEqual(user_attr_list[3],
                             "staff@uw.edu")
            self.assertEqual(user_attr_list[4],
                             "OVP OF UW IT")
            self.assertEqual(user_attr_list[5], "")
            self.assertEqual(user_attr_list[6], "y")
            self.assertEqual(user_attr_list[7], "y")
            self.assertEqual(user_attr_list[8], "n")
            self.assertEqual(user_attr_list[9], "y")
            self.assertEqual(user_attr_list[10], "n")
