from django.conf import settings
from django.test import TransactionTestCase
from sis_provisioner.test import FPWS, FBRI
from sis_provisioner.models import UwBridgeUser, get_now
from sis_provisioner.dao.user import get_user_by_netid
from sis_provisioner.account_managers.bridge_checker import BridgeChecker
from sis_provisioner.account_managers.bridge_worker import BridgeWorker
from sis_provisioner.test.dao.user import new_uw_bridge_test_user


class TestBridgeUserChecker(TransactionTestCase):

    def test_update(self):
        with self.settings(RESTCLIENTS_PWS_DAO_CLASS=FPWS,
                           RESTCLIENTS_PWS_BRIDGE_DAO_CLASS=FBRI):
            user1, person = new_uw_bridge_test_user('javerage')
            user1.save()
            user2, person = new_uw_bridge_test_user('staff')
            user2.save()
            loader = BridgeChecker(BridgeWorker())
            loader.load()
            self.assertEqual(loader.get_total_count(), 3)
            self.assertEqual(loader.get_new_user_count(), 0)
            self.assertEqual(loader.get_loaded_count(), 0)
            self.assertIsNotNone(loader.get_error_report())
            self.assertTrue(loader.has_error())
