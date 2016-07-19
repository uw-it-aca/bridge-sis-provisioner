from restclients.exceptions import DataFailureException
from django.test import TestCase
from sis_provisioner.test import FPWS, FHRP
from sis_provisioner.dao.user import create_user, get_user_from_db,\
    normalize_email


class TestUserDao(TestCase):

    def test_create_user_withhrp(self):
        with self.settings(RESTCLIENTS_PWS_DAO_CLASS=FPWS,
                           RESTCLIENTS_HRPWS_DAO_CLASS=FHRP):
            user = create_user('staff', include_hrp=True)
            self.assertIsNotNone(user)
            self.assertEqual(user.netid, 'staff')
            self.assertEqual(user.regid,
                             "10000000000000000000000000000001")
            self.assertEqual(user.display_name, "James Staff")
            self.assertEqual(user.first_name, "JAMES AVERAGE")
            self.assertEqual(user.last_name, "STAFF")
            self.assertEqual(user.get_sortable_name(), "Staff, James")
            self.assertEqual(user.email, "staff@uw.edu")
            self.assertEqual(user.hrp_home_dept_org_code,
                             "2070001000")
            self.assertEqual(user.hrp_home_dept_org_name,
                             "LIBRARY")
            self.assertEqual(user.hrp_emp_status, 'S')

            user = get_user_from_db('staff')
            self.assertIsNotNone(user)
            self.assertEqual(user.netid, 'staff')
            self.assertEqual(user.regid,
                             "10000000000000000000000000000001")

    def test_create_user(self):
        with self.settings(RESTCLIENTS_PWS_DAO_CLASS=FPWS,
                           RESTCLIENTS_HRPWS_DAO_CLASS=FHRP):
            user = create_user('faculty')
            self.assertIsNotNone(user)
            self.assertEqual(user.netid, 'faculty')
            self.assertIsNone(user.hrp_home_dept_org_code)
            self.assertIsNone(user.hrp_home_dept_org_name)
            self.assertIsNone(user.hrp_emp_status)

    def test_normalize_email(self):
        self.assertEqual(normalize_email("x@uw.edu"), "x@uw.edu")
        self.assertEqual(normalize_email("x@uw.edu."), "x@uw.edu")
        self.assertIsNone(normalize_email(None))

    def test_err_case(self):
        with self.settings(RESTCLIENTS_GWS_DAO_CLASS=FPWS):
            self.assertRaises(DataFailureException,
                              create_user,
                              "supple")
            self.assertIsNone(get_user_from_db("none"))
