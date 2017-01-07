from django.test import TransactionTestCase
from django.db.models import Q
from datetime import timedelta
from restclients.exceptions import DataFailureException
from sis_provisioner.models import UwBridgeUser, get_now,\
    EmployeeAppointment
from sis_provisioner.dao.pws import get_person
from sis_provisioner.dao.hrp import get_appointments
from sis_provisioner.dao.user import normalize_email, normalize_name,\
    _emp_attr_unchanged, filter_by_ids, get_user_by_netid, get_user_by_regid,\
    get_all_users, save_user, _get_netid_changed_user, _changed_regid,\
    _are_all_disabled, _are_all_active, _appointments_json_dump,\
    get_user_from_db, get_total_users, get_user_by_bridgeid
from sis_provisioner.test import fdao_pws_override, fdao_hrp_override
from sis_provisioner.test.dao import mock_uw_bridge_user


@fdao_hrp_override
@fdao_pws_override
class TestUserDao(TransactionTestCase):

    def test_emp_attr_unchanged(self):
        self.assertTrue(_emp_attr_unchanged("[]", "[]"))
        self.assertTrue(_emp_attr_unchanged(None, None))
        self.assertFalse(_emp_attr_unchanged(None, "[]"))
        self.assertFalse(_emp_attr_unchanged(None, ""))
        app = EmployeeAppointment()
        app.load_from_json({"an": 2, "jc": "0191", "oc": "2540574070"})
        self.assertTrue(_emp_attr_unchanged(
                app.json_dump_compact(),
                '{"an":2,"jc":"0191","oc":"2540574070"}'))

    def test_normalize_email(self):
        self.assertEqual(normalize_email("x@uw.edu"), "x@uw.edu")
        self.assertEqual(normalize_email("x@uw.edu."), "x@uw.edu")
        self.assertEqual(normalize_email("x@ uw.edu"), "x@uw.edu")
        self.assertIsNone(normalize_email(None))

    def test_normalize_name(self):
        self.assertEqual(normalize_name("STAFF"), "Staff")
        self.assertEqual(normalize_name("STAFF C"), "Staff C")
        self.assertEqual(normalize_name(None), "")
        self.assertEqual(normalize_name(""), "")

    def test_get(self):
        user, person = mock_uw_bridge_user('staff')
        user.bridge_id = 100
        user.save()

        users = filter_by_ids(person.uwnetid, person.uwregid)
        self.assertEqual(len(users), 1)

        self.assertEqual(get_total_users(), 1)

        users = get_all_users()
        self.assertEqual(len(users), 1)

        users = filter_by_ids(person.uwnetid, None)
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].netid, person.uwnetid)

        user = get_user_by_bridgeid(100)
        self.assertEqual(user.bridge_id, 100)
        self.assertEqual(user.netid, person.uwnetid)

        user = get_user_by_netid(person.uwnetid)
        self.assertEqual(user.netid, person.uwnetid)

        user = get_user_by_regid(person.uwregid)
        self.assertEqual(user.regid, person.uwregid)

        user = get_user_from_db(100, None, None)
        self.assertEqual(user.bridge_id, 100)
        self.assertEqual(user.netid, person.uwnetid)
        self.assertEqual(user.regid, person.uwregid)

        user = get_user_from_db(0, person.uwnetid, None)
        self.assertEqual(user.netid, person.uwnetid)
        self.assertEqual(user.regid, person.uwregid)

        user = get_user_from_db(0, None, person.uwregid)
        self.assertEqual(user.netid, person.uwnetid)
        self.assertEqual(user.regid, person.uwregid)

        user = get_user_by_bridgeid(0)
        self.assertIsNone(user)

        user = get_user_by_netid(None)
        self.assertIsNone(user)

        user = get_user_by_regid(None)
        self.assertIsNone(user)

        user = get_user_from_db(0, None, None)
        self.assertIsNone(user)

    def test_err_case(self):
        self.assertEqual(len(get_all_users()), 0)
        self.assertEqual(len(filter_by_ids(None, None)), 0)
        self.assertIsNone(get_user_by_netid(None))
        self.assertIsNone(get_user_by_regid(None))
        user, user_del = save_user(None)
        self.assertIsNone(user)
        self.assertIsNone(user_del)

    def test_save_user_without_hrp(self):
        person = get_person('faculty')
        self.assertIsNotNone(person)
        user, del_u = save_user(person, include_hrp=False)
        self.assertIsNotNone(user)
        self.assertEqual(user.netid, person.uwnetid)
        self.assertEqual(user.regid, person.uwregid)
        self.assertEqual(user.get_display_name(),
                         "James Faculty")
        self.assertTrue(user.is_new())
        self.assertFalse(user.is_update())
        self.assertEqual(user.email, "")
        self.assertEqual(user.get_email(), "faculty@uw.edu")
        self.assertTrue(user.has_display_name())
        self.assertEqual(user.get_display_name(), 'James Faculty')
        self.assertFalse(user.has_emp_appointments())
        self.assertEqual(user.get_total_emp_apps(), 0)
        users = UwBridgeUser.objects.filter(Q(regid=person.uwregid) |
                                            Q(netid=person.uwnetid))
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0], user)

        # the case of no change
        user, del_u = save_user(person, include_hrp=False)
        self.assertTrue(user.no_action())
        self.assertIsNone(del_u)

        # test restore an disabled
        user.disable()
        user_upd, user_del = save_user(person, include_hrp=False)
        self.assertTrue(user_upd.is_restore())

    def test_save_user_withhrp(self):
        person = get_person('faculty')
        self.assertIsNotNone(person)
        user, del_u = save_user(person, include_hrp=False)
        self.assertIsNone(del_u)
        user, del_u = save_user(person, include_hrp=True)
        self.assertIsNone(del_u)
        self.assertIsNotNone(user)
        self.assertEqual(user.netid, 'faculty')
        self.assertFalse(user.is_new())
        self.assertTrue(user.is_update())
        self.assertTrue(user.has_emp_appointments())
        self.assertEqual(user.get_total_emp_apps(), 1)
        self.assertEqual(user.emp_appointments_data,
                         '[{"an":2,"jc":"0191","oc":"2540574070"}]')
        apps = user.get_emp_appointments()
        self.assertEqual(len(apps), 1)

        # the case of no change
        user, del_u = save_user(person, include_hrp=True)
        self.assertTrue(user.no_action())
        self.assertIsNone(del_u)

        person = get_person('staff')
        user, del_u = save_user(person, include_hrp=True)
        self.assertIsNone(del_u)
        self.assertIsNotNone(user)
        self.assertEqual(user.display_name, "James Staff")
        self.assertEqual(user.first_name, "James Average")
        self.assertEqual(user.last_name, "Staff")
        self.assertTrue(user.has_display_name())
        self.assertEqual(user.get_display_name(), "James Staff")
        self.assertEqual(user.email, "staff@uw.edu")
        self.assertEqual(user.get_email(), "staff@uw.edu")
        self.assertFalse(user.has_emp_appointments())
        self.assertEqual(user.emp_appointments_data, "[]")
        self.assertIsNone(user.get_emp_appointments_json())
        self.assertEqual(len(user.get_emp_appointments()), 0)
        self.assertEqual(user.get_total_emp_apps(), 0)

        person = get_person('botgrad')
        user, del_u = save_user(person, include_hrp=True)
        self.assertIsNone(del_u)
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

        self.assertEqual(user.emp_appointments_data,
                         _appointments_json_dump(person))

    def test_netid_change(self):
        user = UwBridgeUser(netid='old',
                            regid="10000000000000000000000000000006",
                            last_visited_at=get_now(),
                            first_name="Changed",
                            last_name="Netid")
        user.save()
        person = get_person('retiree')
        self.assertIsNotNone(person)
        old_user = _get_netid_changed_user([user], person)
        self.assertEqual(old_user.netid, 'old')
        self.assertFalse(_changed_regid([user], person))

        user_upd, user_del = save_user(person, include_hrp=False)
        self.assertIsNotNone(user_upd)
        self.assertTrue(user_upd.netid_changed())
        self.assertFalse(user_upd.regid_changed())
        self.assertEqual(user_upd.prev_netid, 'old')
        self.assertIsNone(user_del)
        user_upd.delete()

        # the case where user is disabled
        user.disabled = True
        user.save()
        user_upd, user_del = save_user(person, include_hrp=False)
        self.assertIsNotNone(user_upd)
        self.assertTrue(user_upd.netid_changed())
        self.assertEqual(user_upd.prev_netid, 'old')
        self.assertTrue(user_upd.is_restore())
        self.assertIsNone(user_del)

    def test_regid_change(self):
        user = UwBridgeUser(netid='retiree',
                            regid="10000000000000000000000000000009",
                            last_visited_at=get_now(),
                            first_name="Ellen",
                            last_name="Louise")
        user.save()
        person = get_person('retiree')
        old_user = _get_netid_changed_user([user], person)
        self.assertIsNone(old_user)
        self.assertTrue(_changed_regid([user], person))
        user_upd, user_del = save_user(person, include_hrp=False)
        self.assertIsNotNone(user_upd)
        self.assertTrue(user_upd.regid_changed())
        self.assertFalse(user_upd.netid_changed())
        self.assertIsNone(user_del)
        self.assertRaises(Exception,
                          get_user_by_regid,
                          "10000000000000000000000000000009")
        user_upd.delete()

        # user is disabled
        user.disabled = True
        user.save()
        user_upd, user_del = save_user(person, include_hrp=False)
        self.assertIsNotNone(user_upd)
        self.assertTrue(user_upd.is_restore())
        self.assertFalse(user_upd.netid_changed())
        self.assertIsNone(user_del)

    def test_2existing_accounts_with_id_changes(self):
        user1 = UwBridgeUser(netid='staff',
                             regid="10000000000000000000000000000009",
                             last_visited_at=get_now(),
                             first_name="Changed",
                             last_name="Regid")
        user1.save()
        user2 = UwBridgeUser(netid='old',
                             regid="10000000000000000000000000000001",
                             last_visited_at=get_now(),
                             first_name="Changed",
                             last_name="Netid")
        user2.save()
        self.assertTrue(_are_all_active([user1, user2]))
        self.assertFalse(_are_all_disabled([user1, user2]))
        person = get_person('staff')
        self.assertIsNotNone(person)
        old_user = _get_netid_changed_user([user1, user2], person)
        self.assertIsNotNone(old_user)
        self.assertEqual(old_user.netid, 'old')
        self.assertTrue(_changed_regid([user1, user2], person))

        user_upd, user_del = save_user(person, include_hrp=False)
        self.assertIsNotNone(user_upd)
        self.assertFalse(user_upd.regid_changed())
        self.assertTrue(user_upd.is_update())

        self.assertIsNotNone(user_del)
        self.assertEqual(user_del.netid, 'old')
        self.assertRaises(Exception,
                          get_user_by_netid,
                          'old')
        user_upd.delete()

        # both records are disabled
        user1.disabled = True
        user1.save()
        user2.disabled = True
        user2.save()
        self.assertTrue(_are_all_disabled([user1, user2]))
        user_upd, user_del = save_user(person, include_hrp=False)
        self.assertIsNotNone(user_upd)
        self.assertFalse(user_upd.netid_changed())
        self.assertFalse(user_upd.regid_changed())
        self.assertTrue(user_upd.is_restore())
        self.assertIsNone(user_del)
        self.assertRaises(Exception,
                          get_user_by_netid,
                          'old')
        self.assertRaises(Exception,
                          get_user_by_regid,
                          "10000000000000000000000000000009")
        user_upd.delete()

        # the disabled record is with the new netid
        user1.disabled = True
        user1.save()
        user2.disabled = False
        user2.save()
        self.assertFalse(_are_all_active([user1, user2]))
        self.assertFalse(_are_all_disabled([user1, user2]))
        user_upd, user_del = save_user(person, include_hrp=False)
        self.assertIsNotNone(user_upd)
        self.assertTrue(user_upd.netid_changed())
        self.assertFalse(user_upd.regid_changed())
        self.assertFalse(user_upd.is_restore())
        self.assertIsNone(user_del)
        self.assertRaises(Exception,
                          get_user_by_netid,
                          'old')
        self.assertRaises(Exception,
                          get_user_by_regid,
                          "10000000000000000000000000000009")
        user_upd.delete()

        # the disabled record is with the old netid
        user1.disabled = False
        user1.save()
        user2.disabled = True
        user2.save()
        user_upd, user_del = save_user(person, include_hrp=False)
        self.assertIsNotNone(user_upd)
        self.assertTrue(user_upd.is_update())
        self.assertFalse(user_upd.netid_changed())
        self.assertFalse(user_upd.regid_changed())
        self.assertFalse(user_upd.is_restore())
        self.assertIsNone(user_del)
        self.assertRaises(Exception,
                          get_user_by_netid,
                          'old')
        self.assertRaises(Exception,
                          get_user_by_regid,
                          "10000000000000000000000000000009")
        user_upd.delete()
