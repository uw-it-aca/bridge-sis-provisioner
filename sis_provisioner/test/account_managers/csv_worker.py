from django.conf import settings
from django.test import TransactionTestCase
from sis_provisioner.account_managers.csv_worker import CsvWorker
from sis_provisioner.models import ACTION_CHANGE_REGID
from sis_provisioner.test import fdao_pws_override
from sis_provisioner.test.dao.user import mock_uw_bridge_user


@fdao_pws_override
class TestCsvWorker(TransactionTestCase):

    def test_add_new_user(self):
        uw_user, person = mock_uw_bridge_user('javerage')
        worker = CsvWorker()
        worker.add_new_user(uw_user)
        self.assertEqual(worker.get_new_user_count(), 1)

    def test_netid_change_user(self):
        uw_user, person = mock_uw_bridge_user('javerage')
        uw_user.netid = 'changed'
        uw_user.prev_netid = 'javerage'
        worker = CsvWorker()
        worker.update_uid(uw_user)
        self.assertTrue(worker.get_netid_changed_count(), 1)

    def test_regid_change_user(self):
        uw_user, person = mock_uw_bridge_user('javerage')
        uw_user.action_priority = ACTION_CHANGE_REGID
        worker = CsvWorker()
        worker.update_user(uw_user)
        self.assertEqual(worker.get_regid_changed_count(), 1)

    def test_delete_user(self):
        uw_user, person = mock_uw_bridge_user('javerage')
        worker = CsvWorker()
        worker.delete_user(uw_user)
        self.assertEqual(worker.get_deleted_count(), 1)

    def test_restore_user(self):
        uw_user, person = mock_uw_bridge_user('javerage')
        worker = CsvWorker()
        worker.restore_user(uw_user)
        self.assertEqual(worker.get_restored_count(), 1)
