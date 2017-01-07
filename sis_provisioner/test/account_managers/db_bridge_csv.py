
from django.conf import settings
from django.test import TransactionTestCase
from datetime import timedelta
from sis_provisioner.test import fdao_pws_override, fdao_gws_override,\
    fdao_bridge_override
from sis_provisioner.models import UwBridgeUser, get_now
from sis_provisioner.dao.user import get_user_by_netid
from sis_provisioner.account_managers import DISALLOWED, LEFT_UW
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
                            email='javerage@uw.edu',
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
        user = UwBridgeUser(netid='invalidu',
                            regid="0136CCB8F66711D5BE060004AC494FFE",
                            last_visited_at=get_now(),
                            email='invalidu@uw.edu',
                            first_name="Invalid",
                            last_name="User")
        user.save()
        loader = UserUpdater(CsvWorker())

        loader.terminate(user, LEFT_UW)
        self.assertIsNotNone(user.terminate_at)
        self.assertEqual(loader.get_deleted_count(), 0)

        loader.terminate(user, DISALLOWED)
        self.assertEqual(loader.get_deleted_count(), 1)

        user = UwBridgeUser(netid='javerage',
                            regid="0",
                            last_visited_at=get_now() - timedelta(days=15),
                            email='javerage@uw.edu',
                            first_name="James",
                            last_name="Student")
        user.save()
        loader.terminate(user, None)
        self.assertEqual(loader.get_deleted_count(), 2)
