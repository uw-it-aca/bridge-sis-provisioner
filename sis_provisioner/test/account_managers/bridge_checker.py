import logging
from django.test import TransactionTestCase
from sis_provisioner.models import UwBridgeUser, get_now
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
        self.assertEqual(len(bridge_users), 6)
        self.assertEqual(get_regid_from_bridge_user(bridge_users[0]),
                         '9136CCB8F66711D5BE060004AC494FFE')
        self.assertEqual(get_regid_from_bridge_user(bridge_users[1]),
                         '10000000000000000000000000000001')

    def test_changed_attributes(self):
        uw_bri_user1, person = mock_uw_bridge_user('javerage')
        buser1 = mock_bridge_user(
            195, uw_bri_user1.netid, uw_bri_user1.regid,
            uw_bri_user1.get_email(), uw_bri_user1.get_display_name())
        uw_bri_user1.netid = 'changed'
        uw_bri_user1.email = 'changed@washington.edu'
        loader = BridgeChecker(BridgeWorker())
        self.assertTrue(loader.changed_attributes(buser1, uw_bri_user1))
        self.assertTrue(uw_bri_user1.netid_changed())
        self.assertFalse(uw_bri_user1.regid_changed())
        self.assertTrue(loader.changed_attributes(None, uw_bri_user1))

        uw_bri_user1.action_priority = 0

        uw_bri_user1, person = mock_uw_bridge_user('javerage')
        uw_bri_user1.last_name = 'Changed'
        self.assertTrue(loader.changed_attributes(buser1, uw_bri_user1))
        self.assertTrue(uw_bri_user1.is_update())
        self.assertTrue(loader.changed_attributes(buser1, uw_bri_user1))

        buser1 = mock_bridge_user(
            195, uw_bri_user1.netid,
            '9136CCB8F66711D5BE060004AC494FFF',
            uw_bri_user1.get_email(),
            uw_bri_user1.get_display_name())
        self.assertTrue(loader.changed_attributes(buser1, uw_bri_user1))
        self.assertFalse(uw_bri_user1.netid_changed())
        self.assertTrue(uw_bri_user1.regid_changed())
        buser1 = mock_bridge_user(
            195, uw_bri_user1.netid,
            uw_bri_user1.regid,
            uw_bri_user1.get_email(),
            uw_bri_user1.get_display_name())
        self.assertTrue(loader.changed_attributes(buser1, uw_bri_user1))

    def test_update_attribute(self):
        uw_bri_user1, person = mock_uw_bridge_user('javerage')
        buser1 = mock_bridge_user(195,
                                  uw_bri_user1.netid,
                                  uw_bri_user1.regid,
                                  uw_bri_user1.get_email(),
                                  uw_bri_user1.get_display_name())
        loader = BridgeChecker(BridgeWorker())
        # no change
        loader.take_action(person, buser1)
        self.assertEqual(loader.get_loaded_count(), 0)

        # Now the user is already in DB
        loader.take_action(person, buser1, in_db=True)
        self.assertFalse(loader.has_error())
        self.assertEqual(loader.get_loaded_count(), 0)

        # name changed
        user = UwBridgeUser.objects.get(netid='javerage')
        user.display_name = "Old Student"
        user.save()
        loader.take_action(person, buser1, in_db=True)
        self.assertEqual(loader.get_loaded_count(), 1)

    def test_update_netid(self):
        user = UwBridgeUser(netid='changed',
                            regid="9136CCB8F66711D5BE060004AC494FFE",
                            email="changed@uw.edu",
                            last_visited_at=get_now(),
                            display_name="James Changed",
                            last_name="Changed")
        user.save()
        loader = BridgeChecker(BridgeWorker())
        loader.load()
        self.assertEqual(loader.get_netid_changed_count(), 1)
        self.assertEqual(loader.get_loaded_count(), 1)

    def test_update_regid(self):
        user = UwBridgeUser(netid='javerage',
                            regid="0136CCB8F66711D5BE060004AC494FFE",
                            email="changed@uw.edu",
                            last_visited_at=get_now(),
                            display_name="James Changed",
                            last_name="Changed")
        user.save()
        loader = BridgeChecker(BridgeWorker())
        loader.load()
        self.assertEqual(loader.get_regid_changed_count(), 1)
        self.assertEqual(loader.get_loaded_count(), 1)

    def test_update_error(self):
        buser1 = mock_bridge_user(900,
                                  'bridge',
                                  '1111111111',
                                  'bridge.ucla.edu', 'Brifge User')
        loader = BridgeChecker(BridgeWorker())
        loader.take_action(None, buser1)

        self.assertTrue(loader.has_error())
        self.assertEqual(loader.get_loaded_count(), 0)

    def test_load_from_bridge_to_db(self):
        loader = BridgeChecker(BridgeWorker())
        loader.load()
        self.assertEqual(get_total_users(), 3)
        users = UwBridgeUser.objects.all()
        self.assertEqual(users[0].netid, "javerage")
        self.assertEqual(users[0].bridge_id, 195)
        self.assertEqual(users[1].netid, "staff")
        self.assertEqual(users[1].bridge_id, 196)
        self.assertEqual(users[2].netid, "affiemp")
        self.assertEqual(users[2].bridge_id, 198)

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
        user4.regid = "B814EFBC6A7C11D5A4AE0004AC494FFE"
        user4.save()

        loader = BridgeChecker(BridgeWorker())
        loader.load()

        self.assertEqual(get_total_users(), 5)

        self.assertEqual(len(get_users_from_db(
            198, 'affiemp', "10000000000000000000000000000011")), 1)

        self.assertEqual(len(get_users_from_db(
            196, 'staff', "10000000000000000000000000000001")), 1)

        self.assertRaises(UwBridgeUser.DoesNotExist,
                          get_user_by_netid,
                          'seagrad')

        self.assertEqual(
            len(get_users_from_db(
                199, 'unknown', "10000000000000000000000000000000")), 0)

        leftuw = get_user_by_netid('leftuw')
        self.assertEqual(leftuw.bridge_id, 200)
        self.assertTrue(leftuw.has_terminate_date())

        self.assertEqual(loader.get_total_count(), 6)
        self.assertEqual(loader.get_new_user_count(), 0)
        self.assertEqual(loader.get_netid_changed_count(), 0)
        self.assertEqual(loader.get_regid_changed_count(), 0)
        self.assertEqual(loader.get_loaded_count(), 0)
        self.assertIsNotNone(loader.get_error_report())
        self.assertTrue(loader.has_error())
        self.assertEqual(get_total_users(), 5)
