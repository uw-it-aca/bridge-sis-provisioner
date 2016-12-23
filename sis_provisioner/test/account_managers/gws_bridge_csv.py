from django.conf import settings
from django.test import TransactionTestCase
from django.test.utils import override_settings
from restclients.exceptions import DataFailureException
from sis_provisioner.models import UwBridgeUser, get_now, ACTION_RESTORE,\
    ACTION_CHANGE_REGID, ACTION_UPDATE
from sis_provisioner.test import fdao_pws_override, fdao_gws_override,\
    fdao_hrp_override
from sis_provisioner.account_managers.gws_bridge import GwsBridgeLoader
from sis_provisioner.account_managers.csv_worker import CsvWorker


@fdao_hrp_override
@fdao_gws_override
@fdao_pws_override
class TestGwsBridgeCsvLoader(TransactionTestCase):

    def test_load_users_no_hrp(self):
        loader = GwsBridgeLoader(CsvWorker())
        loader.load()
        self.assertEqual(loader.get_total_count(), 11)
        self.assertEqual(loader.get_new_user_count(), 8)
        self.assertEqual(loader.get_loaded_count(), 8)
        self.assertEqual(loader.get_netid_changed_count(), 0)
        self.assertEqual(loader.get_regid_changed_count(), 0)

    def test_load_new_users_with_hrp(self):
        loader = GwsBridgeLoader(CsvWorker(),
                                 include_hrp=True)
        loader.load()
        self.assertEqual(loader.get_total_count(), 11)
        self.assertEqual(loader.get_new_user_count(), 8)
        self.assertEqual(loader.get_loaded_count(), 8)
        self.assertEqual(loader.get_netid_changed_count(), 0)
        self.assertEqual(loader.get_regid_changed_count(), 0)

    def test_error_case(self):
        loader = GwsBridgeLoader(CsvWorker())
        loader.apply_change_to_bridge(None)
        self.assertEqual(loader.get_total_count(), 0)
        self.assertEqual(loader.get_new_user_count(), 0)
        self.assertEqual(loader.get_loaded_count(), 0)
        self.assertEqual(loader.get_netid_changed_count(), 0)
        self.assertEqual(loader.get_regid_changed_count(), 0)

    def test_netid_change_user(self):
        user = UwBridgeUser(netid='changed',
                            bridge_id=195,
                            prev_netid='javerage',
                            regid="9136CCB8F66711D5BE060004AC494FFE",
                            action_priority=ACTION_UPDATE,
                            last_visited_at=get_now(),
                            first_name="Changed",
                            last_name="Netid")
        loader = GwsBridgeLoader(CsvWorker())
        loader.apply_change_to_bridge(user)
        self.assertEqual(loader.get_netid_changed_count(), 1)
        users = loader.worker.get_users_netid_changed()
        self.assertEqual(users[0].netid, "changed")
        self.assertEqual(users[0].prev_netid, "javerage")
        self.assertEqual(users[0].action_priority, ACTION_UPDATE)

    def test_regid_change_user(self):
        user = UwBridgeUser(netid='javerage',
                            regid="0136CCB8F66711D5BE060004AC494FFE",
                            action_priority=ACTION_CHANGE_REGID,
                            last_visited_at=get_now(),
                            first_name="Changed",
                            last_name="Regid")
        loader = GwsBridgeLoader(CsvWorker())
        loader.apply_change_to_bridge(user)
        self.assertEqual(loader.get_regid_changed_count(), 1)
        users = loader.worker.get_users_regid_changed()
        self.assertEqual(users[0].action_priority, ACTION_CHANGE_REGID)

    def test_restore_user(self):
        user = UwBridgeUser(netid='javerage',
                            regid="9136CCB8F66711D5BE060004AC494FFE",
                            last_visited_at=get_now(),
                            action_priority=ACTION_RESTORE,
                            email='javerage@uw.edu',
                            first_name="James",
                            last_name="Changed")
        loader = GwsBridgeLoader(CsvWorker())
        loader.apply_change_to_bridge(user)
        self.assertEqual(loader.get_restored_count(), 1)
        users = loader.worker.get_users_to_restore()
        self.assertEqual(users[0].action_priority, ACTION_RESTORE)
