import logging
from django.test import TransactionTestCase
from sis_provisioner.models import UwBridgeUser, get_now,\
    ACTION_NONE, ACTION_UPDATE
from sis_provisioner.dao.user import get_total_users, get_users_from_db,\
    get_user_by_netid
from sis_provisioner.account_managers import fetch_users_from_bridge
from sis_provisioner.account_managers.bridge_checker import BridgeChecker,\
    get_regid_from_bridge_user
from sis_provisioner.account_managers.bridge_worker import BridgeWorker
from sis_provisioner.test import fdao_pws_override, fdao_gws_override,\
    fdao_bridge_override, mock_uw_bridge_user
from sis_provisioner.test.account_managers import mock_bridge_user


logger = logging.getLogger(__name__)


@fdao_bridge_override
@fdao_gws_override
@fdao_pws_override
class TestBridgeUserChecker(TransactionTestCase):

    def test_fetch_users_from_bridge(self):
        bridge_users = fetch_users_from_bridge(logger)
        self.assertIsNotNone(bridge_users)
        self.assertEqual(len(bridge_users), 7)
        self.assertEqual(get_regid_from_bridge_user(bridge_users[0]),
                         '0136CCB8F66711D5BE060004AC494FFE')
        self.assertEqual(bridge_users[0].netid, 'javerage')
        self.assertEqual(bridge_users[0].bridge_id, 194)
        self.assertEqual(get_regid_from_bridge_user(bridge_users[1]),
                         '9136CCB8F66711D5BE060004AC494FFE')
        self.assertEqual(bridge_users[1].netid, 'changed')
        self.assertEqual(bridge_users[1].bridge_id, 195)
        self.assertEqual(get_regid_from_bridge_user(bridge_users[2]),
                         '10000000000000000000000000000001')

    def test_accounts_match(self):
        uw_bri_user1, person = mock_uw_bridge_user('javerage')
        uw_bri_user1.bridge_id = 195
        uw_bri_user1.action_priority = ACTION_NONE
        buser1 = mock_bridge_user(
            194, uw_bri_user1.netid,
            "0136CCB8F66711D5BE060004AC494FFE",
            uw_bri_user1.get_email(),
            uw_bri_user1.get_display_name())
        loader = BridgeChecker(BridgeWorker())
        self.assertFalse(loader.accounts_match(buser1, uw_bri_user1))

    def test_has_updates(self):
        uw_bri_user1, person = mock_uw_bridge_user('javerage')
        uw_bri_user1.action_priority = ACTION_NONE
        buser1 = mock_bridge_user(
            195,
            uw_bri_user1.netid,
            uw_bri_user1.regid,
            uw_bri_user1.get_email(),
            uw_bri_user1.get_display_name())

        loader = BridgeChecker(BridgeWorker())
        # no change
        need_to_update, user = loader.has_updates(buser1, uw_bri_user1)
        self.assertFalse(need_to_update)

        # attribute changed
        uw_bri_user1.action_priority = ACTION_NONE
        buser1.email = 'changed@washington.edu'
        need_to_update, user = loader.has_updates(buser1, uw_bri_user1)
        self.assertTrue(need_to_update)
        self.assertFalse(user.netid_changed())
        self.assertFalse(user.regid_changed())
        self.assertTrue(user.is_update())

        # netid changed
        uw_bri_user1.action_priority = ACTION_NONE
        buser1.netid = 'changed'
        need_to_update, user = loader.has_updates(buser1, uw_bri_user1)
        self.assertTrue(need_to_update)
        self.assertTrue(user.netid_changed())
        self.assertFalse(user.regid_changed())

        uw_bri_user1.action_priority = ACTION_NONE
        uw_bri_user1.prev_netid = 'changed'
        need_to_update, user = loader.has_updates(buser1, uw_bri_user1)
        self.assertTrue(need_to_update)
        self.assertTrue(user.netid_changed())
        self.assertFalse(user.regid_changed())

        # regid changed
        uw_bri_user1, person = mock_uw_bridge_user('javerage')
        uw_bri_user1.action_priority = ACTION_NONE
        buser1 = mock_bridge_user(
            195,
            uw_bri_user1.netid,
            '0136CCB8F66711D5BE060004AC494FFF',
            uw_bri_user1.get_email(),
            uw_bri_user1.get_display_name())
        need_to_update, user = loader.has_updates(buser1, uw_bri_user1)
        self.assertTrue(need_to_update)
        self.assertFalse(user.netid_changed())
        self.assertTrue(user.regid_changed())

    def test_update_attribute(self):
        uw_bri_user1, person = mock_uw_bridge_user('javerage')
        buser1 = mock_bridge_user(195,
                                  uw_bri_user1.netid,
                                  uw_bri_user1.regid,
                                  uw_bri_user1.get_email(),
                                  uw_bri_user1.get_display_name())
        loader = BridgeChecker(BridgeWorker())

        # save uw_bri_user1 in db
        loader.take_action(person, buser1)
        self.assertEqual(loader.get_loaded_count(), 0)

        # Now the user is already in DB
        loader.take_action(person, buser1, in_db=True)
        self.assertFalse(loader.has_error())
        self.assertEqual(loader.get_loaded_count(), 0)

        # name changed
        buser1.full_name = "Old Student"
        loader.take_action(person, buser1, in_db=True)
        self.assertEqual(loader.get_loaded_count(), 1)

    def test_update_regid(self):
        uw_bri_user1, person = mock_uw_bridge_user('javerage')
        buser = mock_bridge_user(195,
                                 uw_bri_user1.netid,
                                 "0136CCB8F66711D5BE060004AC494FFE",
                                 uw_bri_user1.regid,
                                 uw_bri_user1.get_email(),
                                 uw_bri_user1.get_display_name())
        loader = BridgeChecker(BridgeWorker())
        loader.take_action(person, buser)
        self.assertEqual(loader.get_regid_changed_count(), 1)
        self.assertEqual(loader.get_loaded_count(), 1)

    def test_load_bridge_users_with_empty_db(self):
        loader = BridgeChecker(BridgeWorker())
        loader.load()
        self.assertEqual(get_total_users(), 4)
        self.assertEqual(loader.get_loaded_count(), 2)
        self.assertEqual(loader.get_netid_changed_count(), 1)
        users = UwBridgeUser.objects.all()
        self.assertEqual(users[0].netid, "javerage")
        self.assertEqual(users[0].bridge_id, 195)
        self.assertEqual(users[1].netid, "staff")
        self.assertEqual(users[1].bridge_id, 196)
        self.assertEqual(users[2].netid, "seagrad")
        self.assertEqual(users[2].bridge_id, 197)
        self.assertEqual(users[3].netid, "affiemp")
        self.assertEqual(users[3].bridge_id, 198)

    def test_update_netid(self):
        user = UwBridgeUser(netid='changed',
                            bridge_id=195,
                            regid="9136CCB8F66711D5BE060004AC494FFE",
                            email="changed@uw.edu",
                            last_visited_at=get_now(),
                            display_name="James Changed",
                            last_name="Changed")
        user.save()
        loader = BridgeChecker(BridgeWorker())
        loader.load()
        self.assertEqual(loader.get_netid_changed_count(), 1)
        self.assertEqual(loader.get_loaded_count(), 2)

    def test_update_error(self):
        buser1 = mock_bridge_user(900,
                                  'bridge',
                                  '1111111111',
                                  'bridge.ucla.edu', 'Brifge User')
        loader = BridgeChecker(BridgeWorker())
        loader.take_action(None, buser1)

        self.assertTrue(loader.has_error())
        self.assertEqual(loader.get_loaded_count(), 0)

    def test_load(self):
        user1, person = mock_uw_bridge_user('javerage')
        user1.netid = 'changed'
        user1.bridge_id = 195
        user1.save()

        user2, person = mock_uw_bridge_user('staff')
        user2.email = 'staff@washington.edu'
        user2.bridge_id = 196
        user2.save()

        user3, person = mock_uw_bridge_user('botgrad')
        user3.save()

        user4, person = mock_uw_bridge_user('leftuw')
        user4.save()

        loader = BridgeChecker(BridgeWorker())
        loader.load()

        self.assertEqual(get_total_users(), 6)

        self.assertEqual(
            len(get_users_from_db(
                199, 'unknown', "10000000000000000000000000000000")), 0)

        self.assertEqual(len(get_users_from_db(
            198, 'affiemp', "10000000000000000000000000000011")), 1)

        self.assertEqual(len(get_users_from_db(
            196, 'staff', "10000000000000000000000000000001")), 1)

        leftuw = get_user_by_netid('seagrad')
        self.assertEqual(leftuw.bridge_id, 197)

        leftuw = get_user_by_netid('affiemp')
        self.assertEqual(leftuw.bridge_id, 198)

        leftuw = get_user_by_netid('leftuw')
        self.assertEqual(leftuw.bridge_id, 200)
        self.assertTrue(leftuw.has_terminate_date())

        self.assertEqual(loader.get_total_count(), 7)
        self.assertEqual(loader.get_new_user_count(), 0)
        self.assertEqual(loader.get_netid_changed_count(), 0)
        self.assertEqual(loader.get_regid_changed_count(), 0)
        self.assertEqual(loader.get_loaded_count(), 1)
        self.assertIsNotNone(loader.get_error_report())
        self.assertTrue(loader.has_error())
        self.assertEqual(get_total_users(), 6)
