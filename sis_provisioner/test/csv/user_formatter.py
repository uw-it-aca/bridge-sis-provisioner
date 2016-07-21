from django.conf import settings
from django.test import TransactionTestCase
from django.test.utils import override_settings
from sis_provisioner.test import FPWS, FHRP
from sis_provisioner.csv.user_formatter import get_headers, get_attr_list,\
    get_header_for_user_del
from sis_provisioner.dao.user import create_user


class TestUserFormatter(TransactionTestCase):

    def test_get_headers_for_user_del(self):
        self.assertEqual(len(get_header_for_user_del()), 1)
        self.assertEqual(','.join(get_header_for_user_del()),
                         ("UNIQUE ID"))

    def test_get_headers(self):
        self.assertEqual(len(get_headers()), 9)
        self.assertEqual(','.join(get_headers()),
                         ("UNIQUE ID,NAME,EMAIL,regid," +
                          "alumni,employee,faculty,staff,student"))

        self.assertEqual(len(get_headers(include_hrp=True)), 10)
        self.assertEqual(','.join(get_headers(include_hrp=True)),
                         ("UNIQUE ID,NAME,EMAIL,regid," +
                          "alumni,employee,faculty,staff,student," +
                          "emp home campus"))

    def test_get_attr_list_withhrp(self):
        with self.settings(RESTCLIENTS_PWS_DAO_CLASS=FPWS,
                           RESTCLIENTS_HRPWS_DAO_CLASS=FHRP):
            user, deleted = create_user('staff', include_hrp=True)
            user_attr_list = get_attr_list(user, include_hrp=True)

            self.assertEqual(len(user_attr_list), 10)
            self.assertEqual(user_attr_list[0],
                             "staff@washington.edu")
            self.assertEqual(user_attr_list[1],
                             "James Staff")
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

            user, deleted = create_user('faculty', include_hrp=True)
            user_attr_list = get_attr_list(user, include_hrp=True)

            self.assertEqual(len(user_attr_list), 10)
            self.assertEqual(user_attr_list[0],
                             "faculty@washington.edu")
            self.assertEqual(user_attr_list[1],
                             "James Faculty")
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

            user, deleted = create_user('botgrad', include_hrp=True)
            user_attr_list = get_attr_list(user, include_hrp=True)

            self.assertEqual(len(user_attr_list), 10)
            self.assertEqual(user_attr_list[0],
                             "botgrad@washington.edu")
            self.assertEqual(user_attr_list[9], "Bothell")

            user, deleted = create_user('tacgrad', include_hrp=True)
            user_attr_list = get_attr_list(user, include_hrp=True)

            self.assertEqual(len(user_attr_list), 10)
            self.assertEqual(user_attr_list[0],
                             "tacgrad@washington.edu")
            self.assertEqual(user_attr_list[9], "Tacoma")

    def test_get_attr_list_nohrp(self):
        with self.settings(RESTCLIENTS_PWS_DAO_CLASS=FPWS):

            user, deleted = create_user('staff')
            self.assertIsNotNone(user)
            user_attr_list = get_attr_list(user)
            self.assertEqual(len(user_attr_list), 9)
            self.assertEqual(user_attr_list[0],
                             "staff@washington.edu")

            user, deleted = create_user('faculty')
            user_attr_list = get_attr_list(user)
            self.assertEqual(len(user_attr_list), 9)
            self.assertEqual(user_attr_list[0],
                             "faculty@washington.edu")
            self.assertEqual(user_attr_list[1],
                             "James Faculty")
            self.assertEqual(user_attr_list[2],
                             "faculty@uw.edu")
            self.assertEqual(user_attr_list[3],
                             "10000000000000000000000000000005")
            self.assertEqual(user_attr_list[4], "y")
            self.assertEqual(user_attr_list[5], "y")
            self.assertEqual(user_attr_list[6], "y")
            self.assertEqual(user_attr_list[7], "n")
            self.assertEqual(user_attr_list[8], "n")

            user, deleted = create_user('botgrad')
            user_attr_list = get_attr_list(user)
            self.assertEqual(len(user_attr_list), 9)
            self.assertEqual(user_attr_list[0],
                             "botgrad@washington.edu")

            user, deleted = create_user('tacgrad')
            user_attr_list = get_attr_list(user)
            self.assertEqual(len(user_attr_list), 9)
            self.assertEqual(user_attr_list[0],
                             "tacgrad@washington.edu")
