from django.conf import settings
from django.test import TransactionTestCase
from sis_provisioner.dao.pws import get_person
from sis_provisioner.dao.bridge import get_user_by_uwnetid
from sis_provisioner.account_managers.csv_worker import CsvWorker
from sis_provisioner.tests.account_managers import set_uw_account
from sis_provisioner.tests import fdao_pws_override


@fdao_pws_override
class TestCsvWorker(TransactionTestCase):

    def test_add_new_user(self):
        uw_acc = set_uw_account('javerage')
        person = get_person('javerage')
        worker = CsvWorker()
        worker.add_new_user(uw_acc, person)
        self.assertEqual(worker.get_new_user_count(), 1)

    def test_update_user(self):
        uw_acc = set_uw_account('faculty')
        uw_acc.prev_netid = 'tyler'
        person = get_person('tyler')
        exi, bri_acc = get_user_by_uwnetid('tyler')
        worker = CsvWorker()
        worker.update_user(bri_acc, uw_acc, person)
        self.assertTrue(worker.get_netid_changed_count(), 1)

    def test_delete_user(self):
        exi, bri_acc = get_user_by_uwnetid('javerage')
        worker = CsvWorker()
        worker.delete_user(bri_acc)
        self.assertEqual(worker.get_deleted_count(), 1)

    def test_restore_user(self):
        exi, bri_acc = get_user_by_uwnetid('javerage')
        worker = CsvWorker()
        worker.restore_user(bri_acc)
        self.assertEqual(worker.get_restored_count(), 0)
