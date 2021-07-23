# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TransactionTestCase
from unittest.mock import patch
from sis_provisioner.account_managers.terminate import TerminateUser
from sis_provisioner.account_managers.bridge_worker import BridgeWorker
from sis_provisioner.tests import (
    fdao_pws_override, fdao_gws_override, fdao_bridge_override)
from sis_provisioner.tests.account_managers import set_db_records


@fdao_pws_override
@fdao_gws_override
@fdao_bridge_override
class TestTerminateUser(TransactionTestCase):

    @patch('sis_provisioner.dao.gws._get_start_timestamp',
           return_value=1626215400, spec=True)
    def test_to_check(self, mock_fn):
        loader = TerminateUser(BridgeWorker())
        self.assertEqual(len(loader.fetch_users()), 2)

    @patch('sis_provisioner.dao.gws._get_start_timestamp',
           return_value=1626215400, spec=True)
    def test_update(self, mock_fn):
        set_db_records()
        loader = TerminateUser(BridgeWorker())
        loader.load()
        self.assertEqual(loader.get_total_checked_users(), 2)
        self.assertEqual(loader.get_new_user_count(), 0)
        self.assertEqual(loader.get_netid_changed_count(), 1)
        self.assertEqual(loader.get_deleted_count(), 1)
        self.assertEqual(loader.get_restored_count(), 0)
        self.assertEqual(loader.get_updated_count(), 1)
        self.assertFalse(loader.has_error())
