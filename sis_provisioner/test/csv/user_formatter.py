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
                          "alumni,employee,faculty,staff,student," +
                          "emp_status,emp_home_dept_name,emp_campus_code," +
                          "emp_home_college_code,emp_home_dept_code," +
                          "student_dept_name"))

    def test_get_attr_list(self):
        with self.settings(RESTCLIENTS_PWS_DAO_CLASS=FPWS):

            user = create_user('staff')
            user_attr_list = get_attr_list(user)

            self.assertEqual(len(user_attr_list), 15)
            self.assertEqual(user_attr_list[0],
                             "staff@washington.edu")
            self.assertEqual(user_attr_list[1],
                             "10000000000000000000000000000001")
            self.assertEqual(user_attr_list[2],
                             "Staff, James")
            self.assertEqual(user_attr_list[3],
                             "staff@uw.edu")
            self.assertEqual(user_attr_list[4], "y")
            self.assertEqual(user_attr_list[5], "y")
            self.assertEqual(user_attr_list[6], "n")
            self.assertEqual(user_attr_list[7], "y")
            self.assertEqual(user_attr_list[8], "n")
            self.assertEqual(user_attr_list[9], "S")
            self.assertEqual(user_attr_list[10], "LIBRARY")
            self.assertEqual(user_attr_list[11], "2")
            self.assertEqual(user_attr_list[12], "207")
            self.assertEqual(user_attr_list[13], "2070001000")
            self.assertEqual(user_attr_list[14], "")

            user = create_user('faculty')
            user_attr_list = get_attr_list(user)

            self.assertEqual(len(user_attr_list), 15)
            self.assertEqual(user_attr_list[0],
                             "faculty@washington.edu")
            self.assertEqual(user_attr_list[1],
                             "10000000000000000000000000000005")
            self.assertEqual(user_attr_list[2],
                             "Faculty, James")
            self.assertEqual(user_attr_list[3],
                             "faculty@uw.edu")
            self.assertEqual(user_attr_list[4], "y")
            self.assertEqual(user_attr_list[5], "y")
            self.assertEqual(user_attr_list[6], "y")
            self.assertEqual(user_attr_list[7], "n")
            self.assertEqual(user_attr_list[8], "n")
            self.assertEqual(user_attr_list[9], "R")
            self.assertEqual(user_attr_list[10], "PHYSICS GOF")
            self.assertEqual(user_attr_list[11], "2")
            self.assertEqual(user_attr_list[12], "254")
            self.assertEqual(user_attr_list[13], "2540574070")
            self.assertEqual(user_attr_list[14], "")
