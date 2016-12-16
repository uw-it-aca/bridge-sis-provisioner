from django.conf import settings
from django.test import TransactionTestCase
from sis_provisioner.account_managers.bridge_worker import BridgeWorker
from sis_provisioner.models import ACTION_CHANGE_REGID
from sis_provisioner.test import fdao_pws_override, fdao_bridge_override
from sis_provisioner.test.dao.user import mock_uw_bridge_user


@fdao_pws_override
@fdao_bridge_override
class TestBridgeWorker(TransactionTestCase):

    def test_add_new_user(self):
        uw_user, person = mock_uw_bridge_user('javerage')
        worker = BridgeWorker()
        self.assertTrue(worker.add_new_user(uw_user))
        self.assertEqual(worker.get_new_user_count(), 1)

    def test_netid_change_user(self):
        uw_user, person = mock_uw_bridge_user('javerage')
        uw_user.netid = 'changed'
        uw_user.prev_netid = 'javerage'
        worker = BridgeWorker()
        self.assertTrue(worker.update_uid(uw_user))
        self.assertTrue(worker.get_netid_changed_count(), 1)

        uw_user.bridge_id = 195
        self.assertTrue(worker.update_user(uw_user))
        self.assertEqual(worker.get_netid_changed_count(), 2)

        uw_user.bridge_id = 200
        self.assertFalse(worker.update_user(uw_user))

    def test_regid_change_user(self):
        uw_user, person = mock_uw_bridge_user('javerage')
        uw_user.regid = "0136CCB8F66711D5BE060004AC494FFE"
        uw_user.action_priority = ACTION_CHANGE_REGID
        worker = BridgeWorker()
        self.assertTrue(worker._update_user(uw_user))
        self.assertEqual(worker.get_regid_changed_count(), 1)

        uw_user.netid = 'changed'
        self.assertFalse(worker.update_user(uw_user))

    def test_delete_user(self):
        uw_user, person = mock_uw_bridge_user('javerage')
        worker = BridgeWorker()
        self.assertFalse(worker.delete_user(uw_user))
        self.assertEqual(worker.get_deleted_count(), 0)

        uw_user.bridge_id = 195
        self.assertFalse(worker.delete_user(uw_user))
        self.assertEqual(worker.get_deleted_count(), 0)

        uw_user, person = mock_uw_bridge_user('leftuw')
        uw_user.bridge_id = 200
        self.assertTrue(worker.delete_user(uw_user))
        self.assertEqual(worker.get_deleted_count(), 1)

    def test_restore_user(self):
        uw_user, person = mock_uw_bridge_user('javerage')
        worker = BridgeWorker()
        self.assertTrue(worker.restore_user(uw_user))
        self.assertEqual(worker.get_restored_count(), 1)
        uw_user.bridge_id = 195
        self.assertTrue(worker.restore_user(uw_user))
        self.assertEqual(worker.get_restored_count(), 2)

        uw_user.bridge_id = 200
        self.assertFalse(worker.restore_user(uw_user))
