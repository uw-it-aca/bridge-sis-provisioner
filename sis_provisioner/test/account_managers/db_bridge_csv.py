
from django.conf import settings
from django.test import TransactionTestCase
from datetime import timedelta
from sis_provisioner.test import fdao_pws_override, fdao_gws_override,\
    fdao_bridge_override
from sis_provisioner.models import UwBridgeUser, get_now, GRACE_PERIOD
from sis_provisioner.dao.user import get_user_by_netid
from sis_provisioner.account_managers.db_bridge import UserUpdater
from sis_provisioner.account_managers.csv_worker import CsvWorker


@fdao_bridge_override
@fdao_gws_override
@fdao_pws_override
class TestUserCsvUpdater(TransactionTestCase):

    def test_update(self):
        user = UwBridgeUser(netid='javerage',
                            regid="9136CCB8F66711D5BE060004AC494FFE",
                            last_visited_at=get_now(),
                            email='old@uw.edu',
                            first_name="James",
                            last_name="Changed")
        user.save()
        loader = UserUpdater(CsvWorker())
        loader.load()
        bri_users = loader.get_users_to_process()
        self.assertEqual(len(bri_users), 1)
        self.assertEqual(loader.get_total_count(), 1)
        self.assertEqual(loader.get_new_user_count(), 0)
        self.assertEqual(loader.get_loaded_count(), 1)
        self.assertEqual(loader.get_netid_changed_count(), 0)
        self.assertEqual(loader.get_regid_changed_count(), 0)

    def test_changed_regid(self):
        user = UwBridgeUser(netid='javerage',
                            regid="0136CCB8F66711D5BE060004AC494FFE",
                            last_visited_at=get_now(),
                            email='javerage@uw.edu',
                            first_name="James",
                            last_name="Student")
        user.save()
        loader = UserUpdater(CsvWorker())
        loader.load()
        bri_users = loader.get_users_to_process()
        self.assertEqual(len(bri_users), 1)
        self.assertEqual(loader.get_total_count(), 1)
        self.assertEqual(loader.get_loaded_count(), 0)
        self.assertEqual(loader.get_new_user_count(), 0)
        self.assertEqual(loader.get_netid_changed_count(), 0)
        self.assertEqual(loader.get_regid_changed_count(), 1)

    def test_terminate(self):
        user = UwBridgeUser(
            netid='leftuw',
            regid="B814EFBC6A7C11D5A4AE0004AC494FFE",
            last_visited_at=get_now(),
            email='leftuw@uw.edu',
            first_name="Who",
            last_name="Left")
        user.save()
        loader = UserUpdater(CsvWorker())

        loader.load()
        db_user = get_user_by_netid('leftuw')
        self.assertIsNotNone(db_user.terminate_at)
        self.assertEqual(loader.get_deleted_count(), 0)

        user.terminate_at = get_now() - timedelta(days=(GRACE_PERIOD + 1))
        user.save()
        loader.load()
        self.assertEqual(loader.get_deleted_count(), 1)
