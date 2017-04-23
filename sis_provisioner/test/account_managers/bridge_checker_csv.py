from django.conf import settings
from django.test import TransactionTestCase
from sis_provisioner.test import fdao_pws_override, fdao_gws_override,\
    fdao_bridge_override
from sis_provisioner.models import UwBridgeUser, get_now
from sis_provisioner.dao.user import get_user_by_netid
from sis_provisioner.account_managers.bridge_checker import BridgeChecker
from sis_provisioner.account_managers.csv_worker import CsvWorker
from sis_provisioner.test.dao.user import mock_uw_bridge_user


@fdao_bridge_override
@fdao_gws_override
@fdao_pws_override
class TestBridgeUserCsvChecker(TransactionTestCase):

    def test_update(self):
        loader = BridgeChecker(CsvWorker())
        loader.load()
        self.assertEqual(loader.get_total_count(), 7)
        self.assertEqual(loader.get_new_user_count(), 1)
        self.assertEqual(loader.get_netid_changed_count(), 0)
        self.assertEqual(loader.get_regid_changed_count(), 0)
        self.assertEqual(loader.get_loaded_count(), 3)
