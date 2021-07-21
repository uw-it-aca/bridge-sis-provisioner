# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from datetime import timedelta
from django.test import TransactionTestCase
from sis_provisioner.dao.pws import get_person
from sis_provisioner.models import UwAccount, GRACE_PERIOD, get_now
from sis_provisioner.account_managers.emp_loader import ActiveWkrLoader
from sis_provisioner.account_managers.bridge_worker import BridgeWorker
from sis_provisioner.tests import (
    fdao_pws_override, fdao_gws_override, fdao_bridge_override)
from sis_provisioner.tests.account_managers import (
    set_uw_account, set_db_records, set_db_err_records)


@fdao_bridge_override
@fdao_gws_override
@fdao_pws_override
class TestActiveWkrLoader(TransactionTestCase):

    def test_termination(self):
        # normal case
        uw_acc = set_uw_account("leftuw")
        uw_acc.set_bridge_id(200)
        loader = ActiveWkrLoader(BridgeWorker())
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

        # Having unmatched uwnetid
        uw_acc = set_uw_account("alumni")
        uw_acc.set_bridge_id(199)
        loader.terminate_uw_account(uw_acc)
        self.assertEqual(loader.get_deleted_count(), 1)
        self.assertFalse(UwAccount.get("alumni").disabled)

        # Already deleted in Bridge
        uw_acc = set_uw_account("staff")
        uw_acc.set_bridge_id(196)
        loader.terminate_uw_account(uw_acc)
        self.assertEqual(loader.get_deleted_count(), 1)
        self.assertTrue(UwAccount.get("staff").disabled)

    def test_to_check(self):
        loader = ActiveWkrLoader(BridgeWorker())
        person = get_person("affiemp")
        self.assertTrue(loader.to_check(person))
        person = get_person("leftuw")
        self.assertFalse(loader.to_check(person))
        person = get_person("alumni")
        self.assertFalse(loader.to_check(person))

    def test_update(self):
        set_db_records()
        loader = ActiveWkrLoader(BridgeWorker())
        loader.load()
        self.assertEqual(loader.get_total_count(), 7)
        self.assertEqual(loader.get_total_checked_users(), 4)
        self.assertEqual(loader.get_new_user_count(), 0)
        self.assertEqual(loader.get_netid_changed_count(), 2)
        self.assertEqual(loader.get_deleted_count(), 1)
        self.assertEqual(loader.get_restored_count(), 0)
        self.assertEqual(loader.get_updated_count(), 2)
        self.assertFalse(loader.has_error())
        # ActiveWkrLoader won't resttore staff

    def test_errors(self):
        set_db_err_records()
        loader = ActiveWkrLoader(BridgeWorker())
        loader.load()
        self.assertEqual(loader.get_total_count(), 2)
        self.assertFalse(loader.has_error())
        self.assertEqual(loader.get_new_user_count(), 0)
        self.assertEqual(loader.get_netid_changed_count(), 0)
        self.assertEqual(loader.get_deleted_count(), 0)
        self.assertEqual(loader.get_restored_count(), 0)
        self.assertEqual(loader.get_updated_count(), 0)
