from django.test import TransactionTestCase, TestCase
from django.db.models import Q
from restclients.exceptions import DataFailureException
from sis_provisioner.models import BridgeUser
from sis_provisioner.test import FPWS, FHRP
from sis_provisioner.dao.pws import get_person
from sis_provisioner.dao.user import create_user, save_user,\
    normalize_email, normalize_first_name, delete_user, get_del_users


class TestUserDao(TransactionTestCase):

    def test_normalize_email(self):
        self.assertEqual(normalize_email("x@uw.edu"), "x@uw.edu")
        self.assertEqual(normalize_email("x@uw.edu."), "x@uw.edu")
        self.assertIsNone(normalize_email(None))

    def test_normalize_first_name(self):
        self.assertEqual(normalize_first_name("STAFF"), "STAFF")
        self.assertEqual(normalize_first_name(None), "")
        self.assertEqual(normalize_first_name(""), "")

    def test_save_user_without_hrp(self):
        with self.settings(RESTCLIENTS_PWS_DAO_CLASS=FPWS):
            person = get_person('faculty')
            self.assertIsNotNone(person)
            user, deletes = save_user(person, False)
            self.assertIsNotNone(user)
            self.assertEqual(user.netid, 'faculty')
            self.assertFalse(user.is_priority_import())
            self.assertFalse(user.netid_changed())
            self.assertFalse(user.regid_changed())
            self.assertFalse(user.is_terminated())
            self.assertTrue(user.has_display_name())
            self.assertEqual(user.get_display_name(), 'James Faculty')
            self.assertIsNone(user.hrp_home_dept_org_code)
            self.assertIsNone(user.hrp_emp_status)

    def test_save_user_withhrp(self):
        with self.settings(RESTCLIENTS_PWS_DAO_CLASS=FPWS):
            person = get_person('faculty')
            self.assertIsNotNone(person)
            user, deletes = save_user(person, True)
            self.assertIsNotNone(user)
            self.assertEqual(user.netid, 'faculty')
            self.assertEqual(user.hrp_home_dept_org_code, '2540574070')
            self.assertEqual(user.hrp_emp_status, 'R')

            users = BridgeUser.objects.filter(Q(regid=person.uwregid) |
                                              Q(netid=person.uwnetid))
            deleted = get_del_users(users)
            self.assertIsNotNone(deleted)
            self.assertEqual(len(deleted), 1)
            self.assertEqual(deleted[0], 'faculty')

    def test_create_user_withhrp(self):
        with self.settings(RESTCLIENTS_PWS_DAO_CLASS=FPWS,
                           RESTCLIENTS_HRPWS_DAO_CLASS=FHRP):
            user, deletes = create_user('staff', include_hrp=True)
            self.assertIsNotNone(user)
            self.assertEqual(user.netid, 'staff')
            self.assertEqual(user.regid,
                             "10000000000000000000000000000001")
            self.assertEqual(user.display_name, "James Staff")
            self.assertEqual(user.first_name, "JAMES AVERAGE")
            self.assertEqual(user.last_name, "STAFF")
            self.assertEqual(user.get_display_name(), "James Staff")
            self.assertEqual(user.email, "staff@uw.edu")
            self.assertEqual(user.hrp_home_dept_org_code,
                             "2070001000")
            self.assertEqual(user.hrp_emp_status, 'S')

            user = BridgeUser.objects.get(netid='staff')
            self.assertIsNotNone(user)
            self.assertEqual(user.regid,
                             "10000000000000000000000000000001")
            self.assertEqual(user.hrp_emp_status, 'S')

            deleted = delete_user('staff')
            self.assertIsNotNone(deleted)
            self.assertEqual(deleted[0], 'staff')

    def test_err_case(self):
        with self.settings(RESTCLIENTS_GWS_DAO_CLASS=FPWS):
            user, deleted_list = create_user("supple")
            self.assertIsNone(deleted_list)
            self.assertIsNone(user)
            user, deleted_list = create_user("renamed")
            self.assertIsNone(deleted_list)
            self.assertIsNone(user)
            user, deleted_list = create_user("none")
            self.assertIsNone(deleted_list)
            self.assertIsNone(user)
