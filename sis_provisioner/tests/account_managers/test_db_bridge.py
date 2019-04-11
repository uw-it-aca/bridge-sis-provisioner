from datetime import timedelta
from django.test import TransactionTestCase
from sis_provisioner.dao.bridge import get_user_by_uwnetid
from sis_provisioner.dao.pws import get_person
from sis_provisioner.models import UwAccount, GRACE_PERIOD, get_now
from sis_provisioner.account_managers.db_bridge import UserUpdater
from sis_provisioner.account_managers.bridge_worker import BridgeWorker
from sis_provisioner.tests import (
    fdao_pws_override, fdao_gws_override, fdao_bridge_override)
from sis_provisioner.tests.account_managers import (
    set_uw_account, set_db_records)


@fdao_bridge_override
@fdao_gws_override
@fdao_pws_override
class TestUserUpdater(TransactionTestCase):

    def test_termination(self):
        uw_acc = set_uw_account("leftuw")
        uw_acc.set_bridge_id(200)
        loader = UserUpdater(BridgeWorker())
        loader.process_termination(uw_acc)
        self.assertEqual(loader.get_deleted_count(), 0)
        uw_acc1 = UwAccount.get("leftuw")
        self.assertTrue(uw_acc1.has_terminate_date())
        self.assertFalse(uw_acc1.disabled)

        uw_acc.terminate_at = get_now() - timedelta(days=(GRACE_PERIOD + 1))
        loader.process_termination(uw_acc)
        self.assertEqual(loader.get_deleted_count(), 1)
        uw_acc1 = UwAccount.get("leftuw")
        self.assertTrue(uw_acc.disabled)

    def test_update(self):
        set_db_records()
        loader = UserUpdater(BridgeWorker())
        loader.load()
        self.assertEqual(loader.get_total_count(), 6)
        self.assertEqual(loader.get_new_user_count(), 0)
        self.assertEqual(loader.get_netid_changed_count(), 2)
        self.assertEqual(loader.get_deleted_count(), 1)
        self.assertEqual(loader.get_restored_count(), 0)
        self.assertEqual(loader.get_updated_count(), 2)
        self.assertFalse(loader.has_error())
        # UserUpdater won't resttore staff
