from django.conf import settings
from django.test import TransactionTestCase
from django.test.utils import override_settings
from sis_provisioner.test import FPWS
from sis_provisioner.csv_formatter import header_for_users, csv_for_user
from sis_provisioner.dao.user import create_user


class TestCscFormatter(TransactionTestCase):

    def test_header_for_users(self):
        self.assertEqual(','.join(header_for_users()),
                         ("Unique ID,Regid,Name,Email," +
                          "employee_department,student_department," +
                          "alumni,employee,faculty,staff,student"))

    def test_csv_for_user(self):
        with self.settings(RESTCLIENTS_PWS_DAO_CLASS=FPWS):

            user = create_user('staff')
            user_attr_list = csv_for_user(user)

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
