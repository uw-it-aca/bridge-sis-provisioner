from django.test import TransactionTestCase
from sis_provisioner.dao.pws import get_person
from sis_provisioner.dao.uw_account import get_by_netid
from sis_provisioner.account_managers.bridge_checker import BridgeChecker
from sis_provisioner.account_managers.bridge_worker import BridgeWorker
from sis_provisioner.tests import (
    fdao_gws_override, fdao_pws_override, fdao_bridge_override)
from sis_provisioner.tests.account_managers import (
    set_uw_account, set_db_records)


@fdao_bridge_override
@fdao_gws_override
@fdao_pws_override
class TestBridgeUserChecker(TransactionTestCase):

    def test_fetch_users(self):
        loader = BridgeChecker(BridgeWorker())
        bridge_users = loader.fetch_users()
        self.assertEqual(len(bridge_users), 6)

    def test_take_action(self):
        loader = BridgeChecker(BridgeWorker())
        bri_acc = loader.get_bridge().get_user_by_uwnetid('alumni')
        alumni = get_person('alumni')
        self.assertFalse(loader.in_uw_groups('alumni'))
        loader.take_action(alumni, bri_acc)
        self.assertEqual(loader.get_netid_changed_count(), 0)
        self.assertEqual(loader.get_deleted_count(), 0)
        self.assertEqual(loader.get_restored_count(), 0)
        self.assertEqual(loader.get_updated_count(), 0)
        self.assertFalse(loader.has_error())

        uw_acc = set_uw_account('javerage')
        uw_acc.set_bridge_id(195)
        bri_acc = loader.get_bridge().get_user_by_uwnetid('javerage')
        javerage = get_person('javerage')
        loader.take_action(javerage, bri_acc)
        self.assertEqual(loader.get_netid_changed_count(), 0)
        self.assertEqual(loader.get_deleted_count(), 0)
        self.assertEqual(loader.get_restored_count(), 0)
        self.assertEqual(loader.get_updated_count(), 0)
        self.assertFalse(loader.has_error())
        self.assertEqual(len(loader.get_error_report()), 0)

        uw_acc = set_uw_account('tyler')
        uw_acc.set_bridge_id(198)
        bri_acc = loader.get_bridge().get_user_by_uwnetid('tyler')
        tyler = get_person('tyler')
        loader.take_action(tyler, bri_acc)
        self.assertEqual(loader.get_netid_changed_count(), 1)
        self.assertEqual(loader.get_updated_count(), 1)
        self.assertFalse(loader.has_error())

    def test_load(self):
        loader = BridgeChecker(BridgeWorker())
        set_db_records()
        loader.load()

        alumni = get_by_netid('alumni')
        self.assertEqual(alumni.bridge_id, 199)
        self.assertEqual(loader.get_total_count(), 6)
        self.assertEqual(loader.get_new_user_count(), 0)
        self.assertEqual(loader.get_netid_changed_count(), 2)
        self.assertEqual(loader.get_deleted_count(), 1)
        self.assertEqual(loader.get_restored_count(), 0)
        self.assertEqual(loader.get_updated_count(), 3)
        self.assertEqual(loader.get_error_report(), "")
        self.assertFalse(loader.has_error())
