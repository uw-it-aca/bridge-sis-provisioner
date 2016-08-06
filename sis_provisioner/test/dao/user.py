from django.test import TransactionTestCase, TestCase
from django.db.models import Q
from datetime import timedelta
from restclients.exceptions import DataFailureException
from sis_provisioner.models import BridgeUser, get_now
from sis_provisioner.test import FPWS, FHRP
from sis_provisioner.dao.pws import get_person
from sis_provisioner.dao.hrp import get_appointments
from sis_provisioner.dao.user import create_user, save_user,\
    normalize_email, normalize_first_name, delete_user, get_del_users,\
    get_all_users, emp_attr_not_changed, person_attr_not_changed,\
    appointments_json_dump, changed_regid, changed_netid


class TestUserDao(TransactionTestCase):

    def test_normalize_email(self):
        self.assertEqual(normalize_email("x@uw.edu"), "x@uw.edu")
        self.assertEqual(normalize_email("x@uw.edu."), "x@uw.edu")
        self.assertIsNone(normalize_email(None))

    def test_normalize_first_name(self):
        self.assertEqual(normalize_first_name("STAFF"), "STAFF")
        self.assertEqual(normalize_first_name(None), "")
        self.assertEqual(normalize_first_name(""), "")

    def test_save_terminate_date(self):
        user, deletes = create_user('staff')
        user.save_terminate_date()
        self.assertIsNotNone(user.terminate_date)
        dtime = user.terminate_date - timedelta(days=15)
        self.assertTrue(get_now() < (dtime + timedelta(seconds=3)))
        user.save_terminate_date(graceful=False)
        dtime = user.terminate_date
        self.assertTrue(get_now() < (dtime + timedelta(seconds=3)))

    def test_set_verified(self):
        user, deletes = create_user('staff')
        self.assertFalse(user.no_action())
        user.save_verified()
        user = BridgeUser.objects.get(netid='staff')
        self.assertTrue(user.no_action())
        self.assertTrue(
            get_now() < (user.last_visited_date + timedelta(seconds=3)))

    def test_save_user_without_hrp(self):
        with self.settings(RESTCLIENTS_PWS_DAO_CLASS=FPWS):
            person = get_person('faculty')
            self.assertIsNotNone(person)
            user, deletes = save_user(person, False)
            self.assertIsNotNone(user)
            self.assertEqual(user.netid, 'faculty')
            self.assertTrue(user.is_priority_normal())
            self.assertFalse(user.netid_changed())
            self.assertFalse(user.regid_changed())
            self.assertFalse(user.passed_terminate_date())
            self.assertTrue(user.has_display_name())
            self.assertEqual(user.get_display_name(), 'James Faculty')
            self.assertFalse(user.has_emp_appointments())
            self.assertEqual(user.get_total_emp_apps(), 0)

            person1 = get_person('faculty')
            self.assertTrue(person_attr_not_changed(user, person1))

            person1 = get_person('staff')
            self.assertFalse(person_attr_not_changed(user, person1))

            users = get_all_users()
            self.assertIsNotNone(users)
            self.assertEqual(len(users), 1)

    def test_save_user_withhrp(self):
        with self.settings(RESTCLIENTS_PWS_DAO_CLASS=FPWS):
            person = get_person('faculty')
            self.assertIsNotNone(person)
            user, deletes = save_user(person, True)
            self.assertIsNotNone(user)
            self.assertEqual(user.netid, 'faculty')
            self.assertTrue(user.has_emp_appointments())
            self.assertEqual(user.get_total_emp_apps(), 1)
            self.assertEqual(user.emp_appointments_data,
                             '[{"an":2,"jc":"0191","oc":"2540574070"}]')
            apps = user.get_emp_appointments()
            self.assertEqual(len(apps), 1)
            self.assertEqual(apps[0].app_number, 2)
            self.assertEqual(apps[0].job_class_code, "0191")
            self.assertEqual(apps[0].org_code, "2540574070")

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
            self.assertFalse(user.has_emp_appointments())
            self.assertEqual(user.emp_appointments_data, "[]")
            self.assertIsNone(user.get_emp_appointments_json())
            self.assertEqual(len(user.get_emp_appointments()), 0)
            self.assertEqual(user.get_total_emp_apps(), 0)

            user = BridgeUser.objects.get(netid='staff')
            self.assertIsNotNone(user)
            self.assertEqual(user.regid,
                             "10000000000000000000000000000001")

            user, deletes = create_user('botgrad', include_hrp=True)
            self.assertIsNotNone(user)
            self.assertEqual(user.netid, 'botgrad')
            self.assertEqual(user.regid,
                             "10000000000000000000000000000003")
            self.assertEqual(user.get_display_name(),
                             "Bothell Student")
            self.assertEqual(user.email, "botgrad@uw.edu")
            self.assertTrue(user.has_emp_appointments())
            self.assertEqual(user.get_total_emp_apps(), 3)
            self.assertIsNotNone(user.emp_appointments_data)
            person1 = get_person('botgrad')
            self.assertEqual(user.emp_appointments_data,
                             appointments_json_dump(get_appointments(person1)))
            self.assertEqual(len(user.get_emp_appointments()), 3)

            user, deletes = create_user('faculty', include_hrp=True)
            self.assertIsNotNone(user)
            self.assertEqual(user.netid, 'faculty')
            self.assertEqual(user.regid,
                             "10000000000000000000000000000005")
            self.assertEqual(user.get_display_name(),
                             "James Faculty")
            self.assertEqual(user.email, "")
            self.assertTrue(user.has_emp_appointments())
            self.assertEqual(user.get_total_emp_apps(), 1)
            self.assertTrue(emp_attr_not_changed(
                    user.emp_appointments_data,
                    '[{"an":2,"jc":"0191","oc":"2540574070"}]'))
            self.assertEqual(len(user.get_emp_appointments()), 1)

    def test_emp_attr_not_changed(self):
            self.assertTrue(emp_attr_not_changed("[]", "[]"))
            self.assertTrue(emp_attr_not_changed(None, None))
            self.assertFalse(emp_attr_not_changed(None, "[]"))
            self.assertFalse(emp_attr_not_changed(None, ""))

    def test_delete_user(self):
        with self.settings(RESTCLIENTS_PWS_DAO_CLASS=FPWS,
                           RESTCLIENTS_HRPWS_DAO_CLASS=FHRP):
            # call create again should return nothing
            user, deletes = create_user('staff', include_hrp=True)
            self.assertIsNotNone(user)
            self.assertIsNone(deletes)

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

            users = get_all_users()
            self.assertEqual(len(users), 0)

    def test_netid_change(self):
        with self.settings(RESTCLIENTS_PWS_DAO_CLASS=FPWS):
            user = BridgeUser(netid='renamed',
                              regid="10000000000000000000000000000006",
                              last_visited_date=get_now(),
                              first_name="Ellen Louise",
                              last_name="Renamed")
            user.save()
            person = get_person('retiree')
            self.assertIsNotNone(person)
            self.assertTrue(changed_netid([user], person))
            self.assertFalse(changed_regid([user], person))
            user, deletes = save_user(person, True)
            self.assertIsNotNone(user)
            self.assertTrue(user.netid_changed())
            self.assertFalse(user.regid_changed())
            self.assertEqual(len(deletes), 1)

    def test_regid_change(self):
        with self.settings(RESTCLIENTS_PWS_DAO_CLASS=FPWS):
            user = BridgeUser(netid='retiree',
                              regid="10000000000000000000000000000009",
                              last_visited_date=get_now(),
                              first_name="Ellen Louise",
                              last_name="Renamed")
            user.save()
            person = get_person('retiree')
            self.assertFalse(changed_netid([user], person))
            self.assertTrue(changed_regid([user], person))
            self.assertIsNotNone(person)
            user, deletes = save_user(person, True)
            self.assertIsNotNone(user)
            self.assertTrue(user.regid_changed())
            self.assertFalse(user.netid_changed())
            self.assertEqual(len(deletes), 1)

    def test_netid_regid_change(self):
        with self.settings(RESTCLIENTS_PWS_DAO_CLASS=FPWS):
            user1 = BridgeUser(netid='staff',
                               regid="10000000000000000000000000000009",
                               last_visited_date=get_now(),
                               first_name="Changed",
                               last_name="Regid")
            user1.save()
            user2 = BridgeUser(netid='retiree',
                               regid="10000000000000000000000000000001",
                               last_visited_date=get_now(),
                               first_name="Changed",
                               last_name="Netid")
            user2.save()
            person = get_person('staff')
            self.assertIsNotNone(person)
            self.assertTrue(changed_netid([user1, user2], person))
            self.assertTrue(changed_regid([user1, user2], person))
            user, deletes = save_user(person, True)
            self.assertIsNotNone(user)
            self.assertTrue(user.netid_changed())
            self.assertFalse(user.regid_changed())
            self.assertEqual(len(deletes), 2)
