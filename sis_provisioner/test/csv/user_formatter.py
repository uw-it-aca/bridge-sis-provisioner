from django.conf import settings
from django.test import TransactionTestCase
from django.test.utils import override_settings
from sis_provisioner.test import FPWS
from sis_provisioner.csv.user_formatter import get_headers, get_attr_list
from sis_provisioner.dao.user import create_user


class TestUserFormatter(TransactionTestCase):

    def test_get_headers(self):
        self.assertEqual(len(get_headers()), 9)
        self.assertEqual(','.join(get_headers()),
                         ("UNIQUE ID,NAME,EMAIL,regid," +
                          "alumni,employee,faculty,staff,student"))

        self.assertEqual(len(get_headers(include_emp_data=True)), 10)
        self.assertEqual(','.join(get_headers(include_emp_data=True)),
                         ("UNIQUE ID,NAME,EMAIL,regid," +
                          "alumni,employee,faculty,staff,student," +
                          "emp home campus"))

    def test_get_attr_list(self):
        with self.settings(RESTCLIENTS_PWS_DAO_CLASS=FPWS):

            user = create_user('staff')
            user_attr_list = get_attr_list(user, include_emp_data=True)

            self.assertEqual(len(user_attr_list), 10)
            self.assertEqual(user_attr_list[0],
                             "staff@washington.edu")
            self.assertEqual(user_attr_list[1],
                             "Staff, James Average")
            self.assertEqual(user_attr_list[2],
                             "staff@uw.edu")
            self.assertEqual(user_attr_list[3],
                             "10000000000000000000000000000001")
            self.assertEqual(user_attr_list[4], "y")
            self.assertEqual(user_attr_list[5], "y")
            self.assertEqual(user_attr_list[6], "n")
            self.assertEqual(user_attr_list[7], "y")
            self.assertEqual(user_attr_list[8], "n")
            self.assertEqual(user_attr_list[9], "Seattle")

            user = create_user('faculty')
            user_attr_list = get_attr_list(user, include_emp_data=True)

            self.assertEqual(len(user_attr_list), 10)
            self.assertEqual(user_attr_list[0],
                             "faculty@washington.edu")
            self.assertEqual(user_attr_list[1],
                             "Faculty, James")
            self.assertEqual(user_attr_list[2],
                             "faculty@uw.edu")
            self.assertEqual(user_attr_list[3],
                             "10000000000000000000000000000005")
            self.assertEqual(user_attr_list[4], "y")
            self.assertEqual(user_attr_list[5], "y")
            self.assertEqual(user_attr_list[6], "y")
            self.assertEqual(user_attr_list[7], "n")
            self.assertEqual(user_attr_list[8], "n")
            self.assertEqual(user_attr_list[9], "Seattle")

            user = create_user('botgrad')
            user_attr_list = get_attr_list(user, include_emp_data=True)

            self.assertEqual(len(user_attr_list), 10)
            self.assertEqual(user_attr_list[0],
                             "botgrad@washington.edu")
            self.assertEqual(user_attr_list[9], "Bothell")

            user = create_user('tacgrad')
            user_attr_list = get_attr_list(user, include_emp_data=True)

            self.assertEqual(len(user_attr_list), 10)
            self.assertEqual(user_attr_list[0],
                             "tacgrad@washington.edu")
            self.assertEqual(user_attr_list[9], "Tacoma")
