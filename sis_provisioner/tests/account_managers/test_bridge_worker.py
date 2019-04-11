import logging
from django.test import TransactionTestCase
from sis_provisioner.dao import DataFailureException
from sis_provisioner.dao.bridge import get_user_by_uwnetid
from sis_provisioner.dao.uw_account import get_by_netid
from sis_provisioner.dao.pws import get_person
from sis_provisioner.account_managers.bridge_worker import BridgeWorker
from sis_provisioner.tests import (
    fdao_pws_override, fdao_bridge_override)
from sis_provisioner.tests.account_managers import set_uw_account


@fdao_pws_override
@fdao_bridge_override
class TestBridgeWorker(TransactionTestCase):

    def test_add_new_user(self):
        worker = BridgeWorker()
        uw_acc = set_uw_account('affiemp')
        person = get_person('affiemp')
        worker.add_new_user(uw_acc, person)
        self.assertEqual(worker.get_new_user_count(), 1)

        worker.add_new_user(set_uw_account('javerage'),
                            get_person('javerage'))
        self.assertTrue(worker.has_err())

    def test_delete_user(self):
        exists, bri_acc = get_user_by_uwnetid('retiree')
        worker = BridgeWorker()
        self.assertTrue(worker.delete_user(bri_acc))
        self.assertEqual(worker.get_deleted_count(), 1)

        bri_acc.bridge_id = 0
        self.assertFalse(worker.delete_user(bri_acc))
        self.assertTrue(worker.has_err())

    def test_restore_user(self):
        uw_acc = set_uw_account('staff')
        uw_acc.set_bridge_id(196)
        worker = BridgeWorker()
        bri_acc = worker.restore_user(uw_acc)
        self.assertIsNotNone(bri_acc)
        self.assertFalse(uw_acc.disabled)
        self.assertEqual(worker.get_restored_count(), 1)

        self.assertIsNone(worker.restore_user(set_uw_account('javerage')))
        self.assertTrue(worker.has_err())

    def test_update_uid(self):
        worker = BridgeWorker()
        uw_acc = set_uw_account('faculty')
        uw_acc.prev_netid = 'tyler'
        uw_acc.set_bridge_id(198)
        self.assertTrue(uw_acc.netid_changed())
        worker.update_uid(uw_acc)
        self.assertEqual(worker.get_netid_changed_count(), 1)
        self.assertFalse(worker.has_err())

        self.assertRaises(DataFailureException,
                          worker.update_uid, set_uw_account('javerage'))

    def test_update_user_with_uid_change(self):
        worker = BridgeWorker()

        uw_acc = set_uw_account('faculty')
        uw_acc.prev_netid = 'tyler'
        uw_acc.set_bridge_id(198)
        self.assertTrue(uw_acc.netid_changed())
        person = get_person('faculty')
        exist, bri_acc = get_user_by_uwnetid('tyler')
        worker.update_user(bri_acc, uw_acc, person)
        self.assertEqual(worker.get_netid_changed_count(), 1)
        self.assertEqual(worker.get_updated_count(), 1)

        uw_acc = set_uw_account('retiree')
        uw_acc.prev_netid = 'ellen'
        uw_acc.set_bridge_id(194)
        self.assertTrue(uw_acc.netid_changed())
        person = get_person('retiree')
        exist, bri_acc = get_user_by_uwnetid('ellen')
        worker.update_user(bri_acc, uw_acc, person)
        self.assertEqual(worker.get_netid_changed_count(), 2)
        self.assertEqual(worker.get_updated_count(), 2)

    def test_update_user_wo_uid_change(self):
        worker = BridgeWorker()
        uw_acc = set_uw_account('staff')
        uw_acc.set_bridge_id(196)
        person = get_person('staff')
        bri_acc = worker.restore_user(uw_acc)
        worker.update_user(bri_acc, uw_acc, person)
        self.assertEqual(worker.get_netid_changed_count(), 0)
        self.assertEqual(worker.get_updated_count(), 1)
