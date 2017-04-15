from django.conf import settings
from django.test import TransactionTestCase
from datetime import timedelta
from sis_provisioner.test import fdao_pws_override, fdao_gws_override,\
    fdao_bridge_override
from sis_provisioner.models import UwBridgeUser, get_now, GRACE_PERIOD
from sis_provisioner.dao.user import get_user_by_netid, get_user_by_regid
from sis_provisioner.account_managers import DISALLOWED, LEFT_UW
from sis_provisioner.account_managers.db_bridge import UserUpdater
from sis_provisioner.account_managers.bridge_worker import BridgeWorker


@fdao_bridge_override
@fdao_gws_override
@fdao_pws_override
class TestUserUpdater(TransactionTestCase):

    def test_update(self):
        user = UwBridgeUser(netid='javerage',
                            regid="9136CCB8F66711D5BE060004AC494FFE",
                            last_visited_at=get_now(),
                            email='javerage@uw.edu',
                            display_name="James Changed",
                            last_name="Changed")
        user.save()
        loader = UserUpdater(BridgeWorker())

        bri_users = loader.fetch_users()
        self.assertEqual(len(bri_users), 1)
        self.assertEqual(bri_users[0].netid, 'javerage')

        loader.load()
        self.assertEqual(loader.get_total_count(), 1)
        self.assertEqual(loader.get_new_user_count(), 0)
        self.assertEqual(loader.get_loaded_count(), 1)
        self.assertEqual(loader.get_netid_changed_count(), 0)
        self.assertEqual(loader.get_regid_changed_count(), 0)
        self.assertFalse(loader.has_error())

    def test_changed_netid(self):
        user = UwBridgeUser(netid='changed',
                            regid="9136CCB8F66711D5BE060004AC494FFE",
                            last_visited_at=get_now(),
                            email='javerage@uw.edu',
                            first_name="James",
                            last_name="Student")
        user.save()
        loader = UserUpdater(BridgeWorker())
        loader.load()
        self.assertEqual(loader.get_total_count(), 1)
        self.assertEqual(loader.get_new_user_count(), 0)
        self.assertEqual(loader.get_netid_changed_count(), 1)
        self.assertEqual(loader.get_regid_changed_count(), 0)

    def test_changed_regid(self):
        user = UwBridgeUser(netid='javerage',
                            regid="0136CCB8F66711D5BE060004AC494FFE",
                            last_visited_at=get_now(),
                            email='javerage@uw.edu',
                            first_name="James",
                            last_name="Changed")
        user.save()
        loader = UserUpdater(BridgeWorker())
        loader.load()
        self.assertRaises(UwBridgeUser.DoesNotExist,
                          get_user_by_regid,
                          "0136CCB8F66711D5BE060004AC494FFE")
        self.assertEqual(loader.get_total_count(), 1)
        self.assertEqual(loader.get_new_user_count(), 0)
        self.assertEqual(loader.get_loaded_count(), 1)
        self.assertEqual(loader.get_regid_changed_count(), 1)

    def test_terminate(self):
        loader = UserUpdater(BridgeWorker())
        user = UwBridgeUser(
            netid='leftuw',
            regid="B814EFBC6A7C11D5A4AE0004AC494FFE",
            last_visited_at=get_now(),
            email='leftuw@uw.edu',
            first_name="Who",
            last_name="Left")
        user.save()

        loader.load()
        buser = get_user_by_netid('leftuw')
        self.assertIsNotNone(buser.terminate_at)
        self.assertEqual(loader.get_deleted_count(), 0)

        user.terminate_at = get_now() - timedelta(days=(GRACE_PERIOD + 1))
        user.bridge_id = 200
        user.disabled = False
        user.save()
        loader.load()
        self.assertEqual(loader.get_deleted_count(), 1)

    def test_invaliduser(self):
        user = UwBridgeUser(
            netid='invaliduser',
            regid="1814EFBC6A7C11D5A4AE0004AC494FFE",
            last_visited_at=get_now() - timedelta(days=GRACE_PERIOD),
            email='invaliduser@uw.edu',
            first_name="Old",
            last_name="User")
        user.save()
        loader = UserUpdater(BridgeWorker())
        loader.load()
        self.assertRaises(UwBridgeUser.DoesNotExist,
                          get_user_by_netid,
                          'invaliduser')
        self.assertEqual(loader.get_deleted_count(), 0)

    def test_error(self):
        loader = UserUpdater(BridgeWorker())
        user = UwBridgeUser(
            netid='renamed',
            regid="10000000000000000000000000000000",
            last_visited_at=get_now(),
            email='unknown',
            first_name="Who",
            last_name="Unknown")
        user.save()
        loader.load()
        self.assertTrue(loader.has_error())
        self.assertRaises(UwBridgeUser.DoesNotExist,
                          get_user_by_netid,
                          'unknown')
        self.assertEqual(loader.get_deleted_count(), 0)
