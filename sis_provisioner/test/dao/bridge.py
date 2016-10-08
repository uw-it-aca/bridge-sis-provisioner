from django.test import TestCase
from restclients.exceptions import DataFailureException
from sis_provisioner.models import UwBridgeUser, get_now
from sis_provisioner.dao.bridge import _get_bridge_user_to_add,\
    add_bridge_user, _get_bridge_user_to_upd, change_uwnetid,\
    delete_bridge_user, get_bridge_user, update_bridge_user,\
    get_all_bridge_users, restore_bridge_user
from sis_provisioner.test import FPWS, FBRI
from sis_provisioner.test.dao.user import new_uw_bridge_test_user


class TestBridgeDao(TestCase):

    def test_get_bridge_user_to_add(self):
        with self.settings(RESTCLIENTS_PWS_DAO_CLASS=FPWS):
            user, person = new_uw_bridge_test_user('staff')
            bridge_user = _get_bridge_user_to_add(user)
            self.assertEqual(
                bridge_user.to_json_post(),
                {'users': [
                  {'first_name': user.first_name.title(),
                   'last_name': user.last_name.title(),
                   'full_name': user.get_display_name(),
                   'email': user.email,
                   'uid': user.netid + '@uw.edu',
                   'custom_fields': [
                      {'value': user.regid,
                       'custom_field_id': '5'}]
                   }]})

    def test_add_bridge_user(self):
        with self.settings(RESTCLIENTS_PWS_DAO_CLASS=FPWS,
                           RESTCLIENTS_BRIDGE_DAO_CLASS=FBRI):
            uw_user, person = new_uw_bridge_test_user('staff')
            self.assertEqual(uw_user.bridge_id, 0)
            busers = add_bridge_user(uw_user)
            self.assertEqual(len(busers), 1)
            buser = busers[0]
            self.assertEqual(buser.bridge_id, 1)
            self.assertEqual(buser.get_uid(),
                             (person.uwnetid + "@uw.edu"))
            self.assertEqual(buser.custom_fields[0].value_id, "1")
            self.assertEqual(buser.custom_fields[0].value, person.uwregid)
            self.assertEqual(buser.custom_fields[0].field_id, '5')
            uw_user1 = _get_bridge_user_to_add(uw_user)

    def test_delete_bridge_user(self):
        with self.settings(RESTCLIENTS_PWS_DAO_CLASS=FPWS,
                           RESTCLIENTS_BRIDGE_DAO_CLASS=FBRI):
            uw_user, person = new_uw_bridge_test_user('javerage')
            self.assertEqual(uw_user.bridge_id, 0)
            self.assertTrue(delete_bridge_user(uw_user))
            uw_user.bridge_id = 195
            self.assertTrue(delete_bridge_user(uw_user))

            uw_user, person = new_uw_bridge_test_user('staff')
            self.assertRaises(DataFailureException,
                              delete_bridge_user,
                              uw_user)
            uw_user.bridge_id = 196
            self.assertRaises(DataFailureException,
                              delete_bridge_user,
                              uw_user)

    def test_get_all_bridge_users(self):
        with self.settings(RESTCLIENTS_PWS_DAO_CLASS=FPWS,
                           RESTCLIENTS_BRIDGE_DAO_CLASS=FBRI):
            busers = get_all_bridge_users(include_course_summary=True)
            self.assertEqual(len(busers), 3)
            buser = busers[0]
            self.assertEqual(buser.bridge_id, 195)
            self.assertEqual(buser.netid, 'javerage')
            buser = busers[1]
            self.assertEqual(buser.bridge_id, 196)
            self.assertEqual(buser.netid, 'staff')
            buser = busers[2]
            self.assertEqual(buser.bridge_id, 197)
            self.assertEqual(buser.netid, 'seagrad')

    def test_get_bridge_user(self):
        with self.settings(RESTCLIENTS_PWS_DAO_CLASS=FPWS,
                           RESTCLIENTS_BRIDGE_DAO_CLASS=FBRI):
            uw_user, person = new_uw_bridge_test_user('javerage')
            busers = get_bridge_user(uw_user)
            self.assertEqual(len(busers), 1)
            buser = busers[0]
            self.assertEqual(buser.bridge_id, 195)
            self.assertEqual(buser.netid, person.uwnetid)
            self.assertEqual(buser.full_name, 'James Student')
            self.assertEqual(len(buser.custom_fields), 1)
            self.assertEqual(buser.custom_fields[0].value_id, '1')
            self.assertEqual(buser.custom_fields[0].field_id, '5')
            self.assertEqual(buser.custom_fields[0].value, person.uwregid)
            uw_user.bridge_id = 195
            busers = get_bridge_user(uw_user)
            self.assertEqual(len(busers), 1)
            buser = busers[0]
            self.assertEqual(buser.bridge_id, 195)
            self.assertEqual(buser.netid, person.uwnetid)

    def test_get_bridge_user_to_upd(self):
        with self.settings(RESTCLIENTS_PWS_DAO_CLASS=FPWS,
                           RESTCLIENTS_BRIDGE_DAO_CLASS=FBRI):
            uw_user, person = new_uw_bridge_test_user('javerage')
            busers = get_bridge_user(uw_user)
            buser0 = busers[0]
            self.assertEqual(buser0.bridge_id, 195)
            self.assertEqual(buser0.netid, person.uwnetid)
            self.assertEqual(buser0.full_name, 'James Student')
            self.assertEqual(buser0.last_name, 'Student')
            uw_user.full_name = 'James Changed'
            uw_user.last_name = 'Changed'
            buser = _get_bridge_user_to_upd(uw_user, buser0)
            self.assertEqual(buser.bridge_id, 195)
            self.assertEqual(buser.netid, person.uwnetid)
            self.assertEqual(buser.full_name, uw_user.full_name)
            self.assertEqual(buser.last_name, uw_user.last_name)
            self.assertEqual(len(buser.custom_fields), 1)
            self.assertIsNotNone(buser.custom_fields[0].value_id)
            #  changed custom field
            uw_user.regid = "0136CCB8F66711D5BE060004AC494FFE"
            uw_user.set_action_regid_changed()
            buser = _get_bridge_user_to_upd(uw_user, buser0)
            self.assertEqual(buser.bridge_id, 195)
            self.assertEqual(buser.netid, person.uwnetid)
            self.assertEqual(buser.full_name, uw_user.full_name)
            self.assertEqual(buser.last_name, uw_user.last_name)
            self.assertEqual(len(buser.custom_fields), 1)
            self.assertIsNone(buser.custom_fields[0].value_id)
            self.assertEqual(buser.custom_fields[0].value, uw_user.regid)

    def test_update_bridge_user(self):
        with self.settings(RESTCLIENTS_PWS_DAO_CLASS=FPWS,
                           RESTCLIENTS_BRIDGE_DAO_CLASS=FBRI):
            uw_user, person = new_uw_bridge_test_user('javerage')
            busers = get_bridge_user(uw_user)
            buser0 = busers[0]
            self.assertEqual(buser0.bridge_id, 195)
            uw_user.full_name = 'James Changed'
            uw_user.last_name = 'Changed'
            uw_user.regid = "0136CCB8F66711D5BE060004AC494FFE"
            uw_user.set_action_regid_changed()
            busers = update_bridge_user(uw_user)
            self.assertEqual(len(busers), 1)
            buser = busers[0]
            self.assertEqual(buser.bridge_id, 195)
            self.assertEqual(buser.netid, person.uwnetid)
            self.assertEqual(buser.full_name, uw_user.full_name)
            self.assertEqual(buser.last_name, uw_user.last_name)
            self.assertEqual(len(buser.custom_fields), 1)
            self.assertEqual(buser.custom_fields[0].value, uw_user.regid)

    def test_change_uwnetid(self):
        with self.settings(RESTCLIENTS_PWS_DAO_CLASS=FPWS,
                           RESTCLIENTS_BRIDGE_DAO_CLASS=FBRI):
            uw_user, person = new_uw_bridge_test_user('javerage')
            self.assertFalse(uw_user.bridge_id)
            uw_user.prev_netid = 'javerage'
            uw_user.netid = 'changed'
            busers = change_uwnetid(uw_user)
            self.assertEqual(len(busers), 1)
            buser = busers[0]
            self.assertEqual(buser.bridge_id, 195)
            self.assertEqual(buser.netid, uw_user.netid)
            self.assertNotEqual(buser.netid, person.uwnetid)

            uw_user.bridge_id = 195
            busers = change_uwnetid(uw_user)
            self.assertEqual(len(busers), 1)
            buser = busers[0]
            self.assertEqual(buser.bridge_id, 195)
            self.assertEqual(buser.netid, uw_user.netid)
            self.assertNotEqual(buser.netid, person.uwnetid)

    def test_restore_bridge_user(self):
        with self.settings(RESTCLIENTS_PWS_DAO_CLASS=FPWS,
                           RESTCLIENTS_BRIDGE_DAO_CLASS=FBRI):
            user = UwBridgeUser(netid='javerage',
                                regid="9136CCB8F66711D5BE060004AC494FFE",
                                last_visited_at=get_now(),
                                first_name="James",
                                last_name="Student"
                                )
            busers = restore_bridge_user(user)
            self.assertEqual(len(busers), 1)
            buser = busers[0]
            self.assertEqual(buser.bridge_id, 195)
            self.assertEqual(buser.netid, 'javerage')

            user.bridge_id = 195
            busers = restore_bridge_user(user)
            self.assertEqual(len(busers), 1)
            buser = busers[0]
            self.assertEqual(buser.bridge_id, 195)
            self.assertEqual(buser.netid, 'javerage')
