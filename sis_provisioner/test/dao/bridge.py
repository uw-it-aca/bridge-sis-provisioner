from django.test import TransactionTestCase
from restclients.exceptions import DataFailureException
from sis_provisioner.models import UwBridgeUser, get_now
from sis_provisioner.dao.bridge import _get_bridge_user_to_add,\
    add_bridge_user, _get_bridge_user_to_upd, change_uwnetid,\
    delete_bridge_user, get_bridge_user, update_bridge_user,\
    get_bridge_user_object, get_all_bridge_users, restore_bridge_user,\
    get_regid_from_bridge_user, _no_change, _custom_field_no_change,\
    is_active_user_exist
from sis_provisioner.test import fdao_pws_override, fdao_bridge_override,\
    mock_uw_bridge_user


@fdao_bridge_override
@fdao_pws_override
class TestBridgeDao(TransactionTestCase):

    def test_get_all_bridge_users(self):
        busers = get_all_bridge_users()
        self.assertEqual(len(busers), 7)
        buser = busers[0]
        self.assertEqual(buser.bridge_id, 194)
        self.assertEqual(buser.netid, 'javerage')
        buser = busers[1]
        self.assertEqual(buser.bridge_id, 195)
        self.assertEqual(buser.netid, 'changed')
        buser = busers[2]
        self.assertEqual(buser.bridge_id, 196)
        self.assertEqual(buser.netid, 'staff')
        buser = busers[3]
        self.assertEqual(buser.bridge_id, 197)
        self.assertEqual(buser.netid, 'seagrad')
        buser = busers[4]
        self.assertEqual(buser.bridge_id, 198)
        self.assertEqual(buser.netid, 'affiemp')
        buser = busers[5]
        self.assertEqual(buser.bridge_id, 199)
        self.assertEqual(buser.netid, 'unknown')
        buser = busers[6]
        self.assertEqual(buser.bridge_id, 200)
        self.assertEqual(buser.netid, 'leftuw')

    def test_get_bridge_user_to_add(self):
        user, person = mock_uw_bridge_user('faculty')
        bridge_user = _get_bridge_user_to_add(user)
        self.assertEqual(
            bridge_user.to_json_post(),
            {'users': [
                {'first_name': 'James',
                 'last_name': 'Faculty',
                 'full_name': 'James Faculty',
                 'email': 'faculty@uw.edu',
                 'uid': 'faculty@uw.edu',
                 'custom_fields': [
                     {'value': user.regid,
                      'custom_field_id': '5'}]}]})

    def test_add_bridge_user(self):
        # not exist
        uw_user, person = mock_uw_bridge_user('faculty')
        self.assertEqual(uw_user.bridge_id, 0)

        buser = _get_bridge_user_to_add(uw_user)
        self.assertEqual(buser.netid, 'faculty')
        self.assertEqual(buser.full_name, uw_user.get_display_name())
        self.assertEqual(buser.email, uw_user.get_email())
        self.assertEqual(buser.custom_fields[0].value, person.uwregid)
        self.assertEqual(buser.custom_fields[0].field_id, '5')

        # normal case
        user, exist = add_bridge_user(uw_user)
        self.assertFalse(exist)
        self.assertEqual(user.netid, 'faculty')
        self.assertEqual(user.bridge_id, 201)
        self.assertEqual(len(user.custom_fields), 0)

        # skipped
        uw_user, person = mock_uw_bridge_user('javerage')
        user, exist = add_bridge_user(uw_user)
        self.assertTrue(exist)

        # restored
        uw_user, person = mock_uw_bridge_user('botgrad')
        user, exist = add_bridge_user(uw_user)
        self.assertFalse(exist)
        self.assertIsNotNone(user)

    def test_delete_bridge_user(self):
        # already deleted
        user, person = mock_uw_bridge_user('botgrad')
        user.bridge_id = 203
        self.assertTrue(delete_bridge_user(user, True))

        # normal case
        uw_user = UwBridgeUser(netid='leftuw',
                               regid="B814EFBC6A7C11D5A4AE0004AC494FFE",
                               bridge_id=200,
                               last_visited_at=get_now(),
                               display_name="Who LEFT",
                               first_name="WHO",
                               last_name="LEFT",
                               email="leftuw@uw.edu")
        self.assertTrue(delete_bridge_user(uw_user, True))
        self.assertTrue(delete_bridge_user(uw_user, False))

        uw_user, person = mock_uw_bridge_user('javerage')
        uw_user.bridge_id = 194
        self.assertTrue(delete_bridge_user(uw_user, False))
        self.assertFalse(delete_bridge_user(uw_user, True))

        uw_user, person = mock_uw_bridge_user('staff')
        self.assertRaises(DataFailureException,
                          delete_bridge_user,
                          uw_user, False)
        uw_user.bridge_id = 196
        self.assertRaises(DataFailureException,
                          delete_bridge_user,
                          uw_user, False)

        self.assertRaises(DataFailureException, delete_bridge_user,
                          self.get_mock_user_unknown(), False)

    def test_get_bridge_user(self):
        uw_user, person = mock_uw_bridge_user('javerage')
        busers = get_bridge_user(uw_user)
        self.assertEqual(len(busers), 1)
        buser = busers[0]
        self.assertEqual(buser.bridge_id, 195)
        self.assertEqual(buser.netid, person.uwnetid)
        self.assertEqual(buser.full_name, "James Old Student")
        self.assertEqual(len(buser.custom_fields), 1)
        self.assertEqual(buser.custom_fields[0].value_id, '1')
        self.assertEqual(buser.custom_fields[0].field_id, '5')
        self.assertEqual(buser.custom_fields[0].value,
                         "0136CCB8F66711D5BE060004AC494FFE")

        uw_user.bridge_id = 195
        busers = get_bridge_user(uw_user)
        self.assertEqual(len(busers), 1)
        buser = busers[0]
        self.assertEqual(buser.bridge_id, 195)
        self.assertEqual(buser.netid, 'javerage')
        self.assertEqual(buser.email, 'javerage@uw.edu')
        self.assertEqual(get_regid_from_bridge_user(buser),
                         "9136CCB8F66711D5BE060004AC494FFE")

    def test_get_bridge_user_object(self):
        uw_user, person = mock_uw_bridge_user('javerage')
        bridge_user = get_bridge_user_object(uw_user)
        self.assertEqual(bridge_user.bridge_id, 195)
        self.assertEqual(bridge_user.netid, 'javerage')
        self.assertEqual(bridge_user.email, 'javerage@uw.edu')

        self.assertRaises(DataFailureException, get_bridge_user_object,
                          self.get_mock_user_unknown())

    def test_custom_field_no_change(self):
        uw_user, person = mock_uw_bridge_user('staff')
        uw_user.bridge_id = 196
        bridge_user = get_bridge_user_object(uw_user)
        self.assertTrue(_custom_field_no_change(uw_user, bridge_user))
        self.assertTrue(_no_change(uw_user, bridge_user))

    def test_get_bridge_user_to_upd(self):
        uw_user = UwBridgeUser(netid='javerage',
                               regid="9136CCB8F66711D5BE060004AC494FFE",
                               bridge_id=195,
                               last_visited_at=get_now(),
                               display_name="James Student",
                               first_name="James",
                               last_name="Student",
                               email="javerage@uw.edu")
        buser0 = get_bridge_user_object(uw_user)
        self.assertFalse(buser0.no_learning_history())
        self.assertFalse(_no_change(uw_user, buser0))
        self.assertTrue(_custom_field_no_change(uw_user, buser0))

        buser = _get_bridge_user_to_upd(uw_user, buser0)
        self.assertEqual(
            buser.to_json_patch(),
            {'user': {'id': 195,
                      'last_name': 'Student',
                      'uid': 'javerage@uw.edu',
                      'full_name': 'James Student',
                      'email': 'javerage@uw.edu'}})

    def test_get_bridge_user_to_upd_changed_custom_field(self):
        uw_user, person = mock_uw_bridge_user('javerage')
        bridge_user = get_bridge_user_object(uw_user)
        self.assertFalse(_no_change(uw_user, bridge_user))
        self.assertFalse(_custom_field_no_change(uw_user, bridge_user))
        buser = _get_bridge_user_to_upd(uw_user, bridge_user)
        self.assertEqual(
            buser.to_json_patch(),
            {'user': {
                'first_name': 'James Average',
                'last_name': 'Student',
                'uid': 'javerage@uw.edu',
                'email': 'javerage@uw.edu',
                'full_name': 'James Student',
                'id': 195,
                'custom_fields': [
                    {'value': '9136CCB8F66711D5BE060004AC494FFE',
                     'custom_field_id': '5'}]}})

    def test_change_uwnetid(self):
        uw_user = UwBridgeUser(netid='javerage',
                               prev_netid='changed',
                               regid="9136CCB8F66711D5BE060004AC494FFE",
                               last_visited_at=get_now(),
                               display_name="James Student",
                               email="javerage@uw.edu")
        # normal
        buser = change_uwnetid(uw_user)
        self.assertEqual(buser.bridge_id, 195)
        self.assertEqual(buser.netid, 'javerage')

        # Skipped
        uw_user, person = mock_uw_bridge_user('staff')
        uw_user.bridge_id = 196
        buser = change_uwnetid(uw_user)
        self.assertEqual(buser.netid, 'staff')

        # on a terminated user
        user, person = mock_uw_bridge_user('botgrad')
        user.netid = 'newgrad'
        user.prev_netid = 'botgrad'
        user.bridge_id = 203
        self.assertIsNone(change_uwnetid(user))

        # not match
        user, person = mock_uw_bridge_user('leftuw')
        user.netid = 'newuw'
        user.prev_netid = 'withuw'
        user.bridge_id = 200
        self.assertIsNone(change_uwnetid(user))

        self.assertRaises(DataFailureException, change_uwnetid,
                          self.get_mock_user_unknown())

    def test_restore_bridge_user(self):
        # mornal case
        user, person = mock_uw_bridge_user('botgrad')
        user.bridge_id = 203
        buser = restore_bridge_user(user)
        self.assertEqual(buser.netid, 'botgrad')

        # netid changed
        user, person = mock_uw_bridge_user('tacgrad')
        user.bridge_id = 204
        buser = restore_bridge_user(user)
        self.assertEqual(buser.netid, 'oldgrad')

        # already exists
        uw_user = UwBridgeUser(netid='javerage',
                               regid="0136CCB8F66711D5BE060004AC494FFE",
                               last_visited_at=get_now(),
                               email='javerage@uw.edu',
                               display_name="James Student")
        user = restore_bridge_user(uw_user)
        self.assertEqual(user.netid, 'javerage')
        self.assertEqual(user.bridge_id, 195)

        self.assertRaises(DataFailureException, restore_bridge_user,
                          self.get_mock_user_unknown())

    def test_update_bridge_user(self):
        uw_user, person = mock_uw_bridge_user('javerage')
        self.assertTrue(update_bridge_user(uw_user))

        uw_user, person = mock_uw_bridge_user('staff')
        uw_user.bridge_id = 196
        self.assertIsNone(update_bridge_user(uw_user))

        self.assertRaises(DataFailureException, update_bridge_user,
                          self.get_mock_user_unknown())

    def get_mock_user_unknown(self):
        return UwBridgeUser(netid='invaliduid',
                            regid="0036CCB8F66711D5BE060004AC494FFE",
                            last_visited_at=get_now(),
                            first_name="James",
                            last_name="Student")

    def test_is_active_user_exist(self):
        exists, user = is_active_user_exist('botgrad')
        self.assertTrue(exists)
        self.assertIsNone(user)

        exists, user = is_active_user_exist('javerage')
        self.assertTrue(exists)
        self.assertEqual(user.bridge_id, 195)

        exists, user2 = is_active_user_exist('unknown')
        self.assertFalse(exists)
        self.assertIsNone(user2)
