from django.conf import settings
from django.test import TransactionTestCase
from django.test.utils import override_settings
from sis_provisioner.test import FPWS, FHRP
from sis_provisioner.csv.user_formatter import get_headers, get_attr_list,\
    get_header_for_user_del, get_campus, get_emp_app_att_list,\
    get_campus_from_org_code, get_coll_from_org_code,\
    get_dept_from_org_code
from sis_provisioner.dao.user import create_user


class TestUserFormatter(TransactionTestCase):

    def test_get_campus(self):
        self.assertEqual(get_campus(1), "")
        self.assertEqual(get_campus(2), "Seattle")
        self.assertEqual(get_campus(3), "Seattle Health Sciences")
        self.assertEqual(get_campus(4), "Seattle")
        self.assertEqual(get_campus(5), "Bothell")
        self.assertEqual(get_campus(6), "Tacoma")

    def test_get_campus_from_org_code(self):
        self.assertEqual(get_campus_from_org_code("2000000000"), "Seattle")
        self.assertEqual(get_campus_from_org_code("3000000000"),
                         "Seattle Health Sciences")
        self.assertEqual(get_campus_from_org_code("4000000000"), "Seattle")
        self.assertEqual(get_campus_from_org_code("5000000000"), "Bothell")
        self.assertEqual(get_campus_from_org_code("6000000000"), "Tacoma")

    def test_get_coll_from_org_code(self):
        self.assertEqual(get_coll_from_org_code("2000000000"), "200")

    def test_get_dept_from_org_code(self):
        self.assertEqual(get_dept_from_org_code("2000000000"), "2000000")

    def test_get_headers_for_user_del(self):
        self.assertEqual(len(get_header_for_user_del()), 1)
        self.assertEqual(','.join(get_header_for_user_del()),
                         ("UNIQUE ID"))

    def test_get_emp_app_att_list(self):
        with self.settings(RESTCLIENTS_PWS_DAO_CLASS=FPWS,
                           RESTCLIENTS_HRPWS_DAO_CLASS=FHRP):
            user, deletes = create_user('staff', include_hrp=True)
            self.assertEqual(','.join(
                    get_emp_app_att_list(user.get_emp_appointments())),
                             ',,,,,,,,')

            user, deletes = create_user('botgrad', include_hrp=True)
            emp_attrs = get_emp_app_att_list(user.get_emp_appointments())
            self.assertEqual(len(emp_attrs), 9)
            self.assertEqual(emp_attrs[0], "Bothell")
            self.assertEqual(emp_attrs[1], "520")
            self.assertEqual(emp_attrs[2], "5200005")
            self.assertEqual(emp_attrs[3], "Bothell")
            self.assertEqual(emp_attrs[4], "520")
            self.assertEqual(emp_attrs[5], "5200005")
            self.assertEqual(emp_attrs[6], "Bothell")
            self.assertEqual(emp_attrs[7], "510")
            self.assertEqual(emp_attrs[8], "5100001")

    def test_get_headers(self):
        self.assertEqual(len(get_headers()), 4)
        self.assertEqual(','.join(get_headers()),
                         ("UNIQUE ID,NAME,EMAIL,regid"))
        headers = get_headers(include_hrp=True)
        self.assertEqual(len(headers), 13)
        self.assertEqual(','.join(headers),
                         ("UNIQUE ID,NAME,EMAIL,regid," +
                          "emp campus 1,emp coll 1,emp dept 1," +
                          "emp campus 2,emp coll 2,emp dept 2," +
                          "emp campus 3,emp coll 3,emp dept 3"
                          ))

    def test_get_attr_list_withhrp(self):
        with self.settings(RESTCLIENTS_PWS_DAO_CLASS=FPWS,
                           RESTCLIENTS_HRPWS_DAO_CLASS=FHRP):
            user, deleted = create_user('staff', include_hrp=True)
            user_attr_list = get_attr_list(user, include_hrp=True)
            self.assertEqual(len(user_attr_list), 13)
            self.assertEqual(user_attr_list[0],
                             "staff@uw.edu")
            self.assertEqual(user_attr_list[1],
                             "James Staff")
            self.assertEqual(user_attr_list[2],
                             "staff@uw.edu")
            self.assertEqual(user_attr_list[3],
                             "10000000000000000000000000000001")
            self.assertEqual(user_attr_list[4], "")

            user, deleted = create_user('faculty', include_hrp=True)
            self.assertEqual(user.emp_appointments_data,
                             '[{"an":2,"jc":"0191","oc":"2540574070"}]')
            self.assertEqual(user.get_total_emp_apps(), 1)
            user_attr_list = get_attr_list(user, include_hrp=True)
            self.assertEqual(len(user_attr_list), 13)
            self.assertEqual(user_attr_list[0],
                             "faculty@uw.edu")
            self.assertEqual(user_attr_list[1],
                             "James Faculty")
            self.assertEqual(user_attr_list[2],
                             "faculty@uw.edu")
            self.assertEqual(user_attr_list[3],
                             "10000000000000000000000000000005")
            self.assertEqual(user_attr_list[4], "Seattle")

            user, deleted = create_user('botgrad', include_hrp=True)
            user_attr_list = get_attr_list(user, include_hrp=True)

            self.assertEqual(len(user_attr_list), 13)
            self.assertEqual(user_attr_list[0],
                             "botgrad@uw.edu")
            self.assertEqual(user_attr_list[4], "Bothell")

            user, deleted = create_user('tacgrad', include_hrp=True)
            user_attr_list = get_attr_list(user, include_hrp=True)

            self.assertEqual(len(user_attr_list), 13)
            self.assertEqual(user_attr_list[0],
                             "tacgrad@uw.edu")
            self.assertEqual(user_attr_list[4], "Tacoma")

            user, deleted = create_user('retiree', include_hrp=True)
            user_attr_list = get_attr_list(user, include_hrp=True)
            self.assertEqual(user_attr_list[1], "Ellen Louise Retiree")
            self.assertEqual(user_attr_list[4], "")

            user, deleted = create_user('leftuw', include_hrp=True)
            user_attr_list = get_attr_list(user, include_hrp=True)
            self.assertEqual(user_attr_list[1], "Nina LEFT")
            self.assertEqual(user_attr_list[4], "")

    def test_get_attr_list_nohrp(self):
        with self.settings(RESTCLIENTS_PWS_DAO_CLASS=FPWS):

            user, deleted = create_user('staff')
            self.assertIsNotNone(user)
            user_attr_list = get_attr_list(user)
            self.assertEqual(len(user_attr_list), 4)
            self.assertEqual(user_attr_list[0],
                             "staff@uw.edu")

            user, deleted = create_user('faculty')
            user_attr_list = get_attr_list(user)
            self.assertEqual(len(user_attr_list), 4)
            self.assertEqual(user_attr_list[0],
                             "faculty@uw.edu")
            self.assertEqual(user_attr_list[1],
                             "James Faculty")
            self.assertEqual(user_attr_list[2],
                             "faculty@uw.edu")
            self.assertEqual(user_attr_list[3],
                             "10000000000000000000000000000005")

            user, deleted = create_user('botgrad')
            user_attr_list = get_attr_list(user)
            self.assertEqual(len(user_attr_list), 4)
            self.assertEqual(user_attr_list[0],
                             "botgrad@uw.edu")

            user, deleted = create_user('tacgrad')
            user_attr_list = get_attr_list(user)
            self.assertEqual(len(user_attr_list), 4)
            self.assertEqual(user_attr_list[0],
                             "tacgrad@uw.edu")
