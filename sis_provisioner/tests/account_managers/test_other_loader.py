# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TransactionTestCase
from sis_provisioner.dao.pws import get_person
from sis_provisioner.dao.uw_account import get_all_uw_accounts
from sis_provisioner.account_managers.other_loader import OtherUserLoader
from sis_provisioner.account_managers.bridge_worker import BridgeWorker
from sis_provisioner.tests import (
    fdao_pws_override, fdao_gws_override, fdao_bridge_override)
from sis_provisioner.tests.account_managers import (
    set_db_records, set_db_err_records)


@fdao_pws_override
@fdao_gws_override
@fdao_bridge_override
class TestOtherUserLoader(TransactionTestCase):

    def test_to_check(self):
        loader = OtherUserLoader(BridgeWorker())
        person = get_person("retiree")
        self.assertFalse(loader.to_check(person))
        person = get_person("leftuw")
        self.assertTrue(loader.to_check(person))

    def test_update(self):
        set_db_records()
        loader = OtherUserLoader(BridgeWorker())
        loader.load()
        self.assertEqual(loader.get_total_checked_users(), 1)
        self.assertEqual(loader.get_new_user_count(), 0)
        self.assertEqual(loader.get_netid_changed_count(), 0)
        self.assertEqual(loader.get_deleted_count(), 0)
        self.assertEqual(loader.get_restored_count(), 0)
        self.assertEqual(loader.get_updated_count(), 0)
        self.assertFalse(loader.has_error())

    def test_errors(self):
        set_db_err_records()
        loader = OtherUserLoader(BridgeWorker())
        loader.load()
        self.assertEqual(loader.get_total_checked_users(), 1)
        self.assertTrue(loader.has_error())
