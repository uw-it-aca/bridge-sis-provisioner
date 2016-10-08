from django.conf import settings
from django.test import TransactionTestCase
from django.test.utils import override_settings
from restclients.exceptions import DataFailureException
from sis_provisioner.models import UwBridgeUser, get_now, ACTION_RESTORE,\
    ACTION_CHANGE_REGID, ACTION_UPDATE
from sis_provisioner.test import FGWS, FPWS, FHRP
from sis_provisioner.account_managers.gws_bridge import GwsBridgeLoader
from sis_provisioner.account_managers.csv_worker import CsvWorker


class TestGwsBridgeCsvLoader(TransactionTestCase):

    def test_load_users_no_hrp(self):
        with self.settings(RESTCLIENTS_GWS_DAO_CLASS=FGWS,
                           RESTCLIENTS_PWS_DAO_CLASS=FPWS):
            loader = GwsBridgeLoader(CsvWorker())
            loader.load()
            self.assertEqual(loader.get_total_count(), 11)
            self.assertEqual(loader.get_new_user_count(), 8)
            self.assertEqual(loader.get_loaded_count(), 8)
            self.assertEqual(loader.get_netid_changed_count(), 0)
            self.assertEqual(loader.get_regid_changed_count(), 0)

    def test_load_new_users_with_hrp(self):
        with self.settings(RESTCLIENTS_GWS_DAO_CLASS=FGWS,
                           RESTCLIENTS_PWS_DAO_CLASS=FPWS,
                           RESTCLIENTS_HRPWS_DAO_CLASS=FHRP):
            loader = GwsBridgeLoader(CsvWorker(),
                                     include_hrp=True)
            loader.load()
            self.assertEqual(loader.get_total_count(), 11)
            self.assertEqual(loader.get_new_user_count(), 8)
            self.assertEqual(loader.get_loaded_count(), 8)
            self.assertEqual(loader.get_netid_changed_count(), 0)
            self.assertEqual(loader.get_regid_changed_count(), 0)

    def test_error_case(self):
        with self.settings(RESTCLIENTS_GWS_DAO_CLASS=FGWS,
                           RESTCLIENTS_PWS_DAO_CLASS=FPWS):
            loader = GwsBridgeLoader(CsvWorker())
            loader.apply_change_to_bridge(None)
            self.assertEqual(loader.get_total_count(), 0)
            self.assertEqual(loader.get_new_user_count(), 0)
            self.assertEqual(loader.get_loaded_count(), 0)
            self.assertEqual(loader.get_netid_changed_count(), 0)
            self.assertEqual(loader.get_regid_changed_count(), 0)

    def test_netid_change_user(self):
        with self.settings(RESTCLIENTS_GWS_DAO_CLASS=FGWS,
                           RESTCLIENTS_PWS_DAO_CLASS=FPWS):
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
            self.assertEqual(loader.get_loaded_count(), 1)

    def test_regid_change_user(self):
        with self.settings(RESTCLIENTS_GWS_DAO_CLASS=FGWS,
                           RESTCLIENTS_PWS_DAO_CLASS=FPWS):
            user = UwBridgeUser(netid='javerage',
                                regid="0136CCB8F66711D5BE060004AC494FFE",
                                action_priority=ACTION_CHANGE_REGID,
                                last_visited_at=get_now(),
                                first_name="Changed",
                                last_name="Regid")
            loader = GwsBridgeLoader(CsvWorker())
            loader.apply_change_to_bridge(user)
            self.assertEqual(loader.get_regid_changed_count(), 1)
            self.assertEqual(loader.get_loaded_count(), 1)

    def test_restore_user(self):
        with self.settings(RESTCLIENTS_GWS_DAO_CLASS=FGWS,
                           RESTCLIENTS_PWS_DAO_CLASS=FPWS):
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
