from django.conf import settings
from django.test import TransactionTestCase
from sis_provisioner.account_managers.bridge_checker import BridgeChecker
from sis_provisioner.account_managers.csv_worker import CsvWorker
from sis_provisioner.tests import fdao_pws_override, fdao_gws_override,\
    fdao_bridge_override


@fdao_bridge_override
@fdao_gws_override
@fdao_pws_override
class TestBridgeUserCsvChecker(TransactionTestCase):

    def test_update(self):
        loader = BridgeChecker(CsvWorker())
        loader.load()
