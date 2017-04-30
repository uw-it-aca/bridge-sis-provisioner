from django.conf import settings
from django.test import TransactionTestCase
from sis_provisioner.models import UwBridgeUser, get_now
from sis_provisioner.account_managers.bridge_worker import BridgeWorker
from sis_provisioner.test import fdao_pws_override, fdao_bridge_override,\
    mock_uw_bridge_user


@fdao_pws_override
@fdao_bridge_override
class TestBridgeWorker(TransactionTestCase):

    def test_add_new_user(self):
        worker = BridgeWorker()
        # exists
        uw_user, person = mock_uw_bridge_user('staff')

        uw_user.set_action_new()
        worker.add_new_user(uw_user)
        self.assertEqual(worker.get_new_user_count(), 0)
        self.assertEqual(worker.get_loaded_count(), 0)

        user = UwBridgeUser.objects.get(netid='staff')
        self.assertTrue(user.no_action())
        self.assertEqual(user.bridge_id, 196)

        # new
        uw_user, person = mock_uw_bridge_user('faculty')
        uw_user.set_action_new()
        worker.add_new_user(uw_user)
        self.assertEqual(worker.get_new_user_count(), 1)
        self.assertEqual(worker.get_loaded_count(), 1)

        user = UwBridgeUser.objects.get(netid='faculty')
        self.assertTrue(user.no_action())
        self.assertEqual(user.bridge_id, 201)

    def get_not_exist_user(self):
        user = UwBridgeUser(netid='notexist',
                            regid="0036CCB8F66711D5BE060004AC494FFE",
                            bridge_id=1200,
                            last_visited_at=get_now(),
                            first_name="Not",
                            last_name="Exist",
                            email="notexist@uw.edu")
        user.save()
        return user

    def test_delete_user(self):
        uw_user, person = mock_uw_bridge_user('javerage')
        worker = BridgeWorker()
        worker.delete_user(uw_user, is_merge=True)
        self.assertEqual(worker.get_deleted_count(), 0)

        uw_user.bridge_id = 195
        worker.delete_user(uw_user, is_merge=True)
        self.assertEqual(worker.get_deleted_count(), 0)

        uw_user, person = mock_uw_bridge_user('leftuw')
        uw_user.bridge_id = 200
        worker.delete_user(uw_user, is_merge=False)
        self.assertEqual(worker.get_deleted_count(), 1)

        user = UwBridgeUser.objects.get(netid='leftuw')
        self.assertTrue(user.no_action())
        self.assertTrue(user.disabled)

        user = UwBridgeUser.objects.get(netid='leftuw')
        self.assertTrue(user.no_action())
        self.assertTrue(user.disabled)

        worker.delete_user(self.get_not_exist_user(), is_merge=False)
        try:
            user = UwBridgeUser.objects.get(netid='notexist')
        except UwBridgeUser.DoesNotExist:
            pass

    def test_netid_change_user(self):
        worker = BridgeWorker()
        uw_user, person = mock_uw_bridge_user('javerage')
        uw_user.prev_netid = 'changed'
        self.assertTrue(worker.update_uid(uw_user))
        self.assertFalse(uw_user.netid_changed())
        self.assertEqual(worker.get_netid_changed_count(), 1)
        self.assertEqual(worker.get_loaded_count(), 0)

        user = UwBridgeUser.objects.get(netid='javerage')
        self.assertTrue(user.no_action())
        self.assertIsNone(user.prev_netid)
        self.assertEqual(user.bridge_id, 195)

        worker = BridgeWorker()
        uw_user, person = mock_uw_bridge_user('javerage')
        uw_user.prev_netid = 'changed'
        uw_user.set_action_update()
        worker.update_user(uw_user)
        self.assertFalse(worker.has_err())
        self.assertEqual(worker.get_netid_changed_count(), 1)
        self.assertEqual(worker.get_loaded_count(), 1)

        user = UwBridgeUser.objects.get(netid='javerage')
        self.assertTrue(user.no_action())
        self.assertIsNone(user.prev_netid)
        self.assertEqual(user.bridge_id, 195)

        uw_user, person = mock_uw_bridge_user('staff')
        uw_user.prev_netid = 'changed'
        self.assertFalse(worker.update_uid(uw_user))
        self.assertTrue(worker.has_err())

        worker = BridgeWorker()
        worker.update_uid(self.get_not_exist_user())
        self.assertEqual(worker.get_netid_changed_count(), 0)
        self.assertEqual(worker.get_loaded_count(), 0)
        try:
            user = UwBridgeUser.objects.get(netid='notexist')
        except UwBridgeUser.DoesNotExist:
            pass

    def test_restore_user(self):
        # normal case
        worker = BridgeWorker()
        uw_user, person = mock_uw_bridge_user('botgrad')
        uw_user.bridge_id = 203
        uw_user.disabled = True
        uw_user.set_action_restore()
        worker.restore_user(uw_user)
        self.assertEqual(worker.get_restored_count(), 1)

        user = UwBridgeUser.objects.get(netid='botgrad')
        self.assertFalse(user.disabled)

        # restored user netid and regid not match
        uw_user = UwBridgeUser(netid='javerage',
                               bridge_id=195,
                               regid="9136CCB8F66711D5BE060004AC494FFE",
                               last_visited_at=get_now(),
                               disabled=True,
                               first_name="James",
                               last_name="Student",
                               email="changed@uw.edu")
        uw_user.set_action_restore()
        worker.restore_user(uw_user)
        self.assertEqual(worker.get_restored_count(), 2)

        user = UwBridgeUser.objects.get(netid='javerage')
        self.assertFalse(user.disabled)
        self.assertTrue(user.no_action())

        worker = BridgeWorker()
        worker.restore_user(self.get_not_exist_user())
        self.assertFalse(worker.has_err())
        self.assertEqual(worker.get_restored_count(), 0)
        try:
            user = UwBridgeUser.objects.get(netid='notexist')
        except UwBridgeUser.DoesNotExist:
            pass

    def test_update_user(self):
        worker = BridgeWorker()
        uw_user, person = mock_uw_bridge_user('staff')
        uw_user.set_action_update()
        worker.update_user(uw_user)
        # no change, skipped
        self.assertEqual(worker.get_netid_changed_count(), 0)
        self.assertEqual(worker.get_regid_changed_count(), 0)
        self.assertEqual(worker.get_loaded_count(), 0)

        uw_user, person = mock_uw_bridge_user('javerage')
        uw_user.set_action_regid_changed()
        worker.update_user(uw_user)
        self.assertEqual(worker.get_netid_changed_count(), 0)
        self.assertEqual(worker.get_regid_changed_count(), 1)
        self.assertEqual(worker.get_loaded_count(), 1)

        uw_user.bridge_id = 195
        uw_user.set_action_regid_changed()
        worker.update_user(uw_user)
        self.assertEqual(worker.get_netid_changed_count(), 0)
        self.assertEqual(worker.get_regid_changed_count(), 2)
        self.assertEqual(worker.get_loaded_count(), 2)

        user = UwBridgeUser.objects.get(netid='javerage')
        self.assertTrue(user.no_action())

    def test__update_user(self):
        uw_user, person = mock_uw_bridge_user('javerage')
        uw_user.regid = "0136CCB8F66711D5BE060004AC494FFE"
        uw_user.set_action_update()
        # regid not change, other attributes changed
        worker = BridgeWorker()
        worker._update_user(uw_user)
        self.assertEqual(worker.get_loaded_count(), 1)
        self.assertEqual(worker.get_regid_changed_count(), 0)

        user = UwBridgeUser.objects.get(netid='javerage')
        self.assertTrue(user.no_action())

        worker = BridgeWorker()
        worker._update_user(self.get_not_exist_user())
        self.assertEqual(worker.get_loaded_count(), 0)
        try:
            user = UwBridgeUser.objects.get(netid='notexist')
        except UwBridgeUser.DoesNotExist:
            pass
