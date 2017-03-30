import logging
from django.test import TransactionTestCase
from sis_provisioner.models import UwBridgeUser, get_now
from sis_provisioner.dao.user import get_total_users, get_user_from_db
from sis_provisioner.account_managers import get_validated_user,\
    fetch_users_from_gws, fetch_users_from_bridge,\
    NO_CHANGE, CHANGED, LEFT_UW, DISALLOWED
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

    def test_get_validated_user(self):
        potential_users = fetch_users_from_gws(logger)
        person, validation_status = get_validated_user(
            logger,
            'staff',
            users_in_gws=potential_users)
        self.assertEqual(person.uwnetid, 'staff')
        self.assertEqual(person.uwregid,
                         '10000000000000000000000000000001')
        self.assertEqual(validation_status, NO_CHANGE)

        person, validation_status = get_validated_user(
            logger,
            'javerage',
            uwregid='10000000000000000000000000000001',
            users_in_gws=potential_users)
        self.assertEqual(person.uwnetid, 'javerage')
        self.assertEqual(person.uwregid,
                         '9136CCB8F66711D5BE060004AC494FFE')
        self.assertEqual(validation_status, CHANGED)

        person, validation_status = get_validated_user(
            logger,
            'unknown',
            uwregid='10000000000000000000000000000000',
            users_in_gws=potential_users)
        self.assertIsNone(person)
        self.assertEqual(validation_status, LEFT_UW)

        person, validation_status = get_validated_user(
            logger,
            'none',
            users_in_gws=potential_users)
        self.assertIsNone(person)
        self.assertEqual(validation_status, DISALLOWED)

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

    def test_actions(self):
        # UwBridgeUser.objects.all().delete()
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

        # netid changed
        loader = BridgeChecker(BridgeWorker())
        UwBridgeUser.objects.all().delete()
        user = UwBridgeUser(netid='changed',
                            regid="9136CCB8F66711D5BE060004AC494FFE",
                            email="changed@uw.edu",
                            last_visited_at=get_now(),
                            display_name="James Changed",
                            last_name="Changed")
        user.save()
        loader.load()
        self.assertEqual(loader.get_netid_changed_count(), 1)
        self.assertEqual(loader.get_loaded_count(), 1)

        # regid changed
        loader = BridgeChecker(BridgeWorker())
        UwBridgeUser.objects.all().delete()
        user = UwBridgeUser(netid='javerage',
                            regid="0136CCB8F66711D5BE060004AC494FFE",
                            email="changed@uw.edu",
                            last_visited_at=get_now(),
                            display_name="James Changed",
                            last_name="Changed")
        user.save()
        loader.load()
        self.assertEqual(loader.get_regid_changed_count(), 1)
        self.assertEqual(loader.get_loaded_count(), 1)

        # error
        loader = BridgeChecker(BridgeWorker())
        UwBridgeUser.objects.all().delete()
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

        user3, person = mock_uw_bridge_user('seagrad')
        user3.bridge_id = 197
        user3.save()

        loader = BridgeChecker(BridgeWorker())
        loader.load()

        self.assertIsNotNone(get_user_from_db(195, None, None))
        try:
            user = UwBridgeUser.objects.get(netid='seagrad')
        except UwBridgeUser.DoesNotExist:
            pass

        user = get_user_from_db(0, 'affiemp', None)
        self.assertEqual(user.bridge_id, 198)

        user = get_user_from_db(196, 'staff', None)
        self.assertEqual(user.bridge_id, 196)

        self.assertIsNone(get_user_from_db(0, 'unknown', None))
        self.assertIsNone(get_user_from_db(0, 'leftuw', None))

        self.assertEqual(loader.get_total_count(), 6)
        self.assertEqual(loader.get_new_user_count(), 0)
        self.assertEqual(loader.get_netid_changed_count(), 0)
        self.assertEqual(loader.get_regid_changed_count(), 0)
        self.assertEqual(loader.get_loaded_count(), 0)
        self.assertIsNotNone(loader.get_error_report())
        self.assertTrue(loader.has_error())
        self.assertEqual(get_total_users(), 3)
