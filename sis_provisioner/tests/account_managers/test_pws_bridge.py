# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TransactionTestCase
from freezegun import freeze_time
from sis_provisioner.dao.pws import get_updated_persons
from sis_provisioner.account_managers.bridge_worker import BridgeWorker
from sis_provisioner.account_managers.pws_bridge import PwsBridgeLoader
from sis_provisioner.tests import (
    fdao_pws_override, fdao_gws_override, fdao_bridge_override)
from sis_provisioner.tests.account_managers import set_db_records


@fdao_bridge_override
@fdao_gws_override
@fdao_pws_override
class TestPwsBridgeLoader(TransactionTestCase):

    @freeze_time("2019-09-01 20:30:00")
    def test_load_pws(self):
        with self.settings(ERRORS_TO_ABORT_LOADER=[],
                           BRIDGE_PERSON_CHANGE_WINDOW=60):
            set_db_records()
            loader = PwsBridgeLoader(BridgeWorker())
            loader.users_to_process = loader.fetch_users()
            self.assertEqual(len(loader.users_to_process), 2)
            loader.process_users()
            self.assertEqual(loader.get_total_count(), 2)
            self.assertEqual(loader.get_total_checked_users(), 2)
            self.assertEqual(loader.get_new_user_count(), 0)
            self.assertEqual(loader.get_restored_count(), 0)
            self.assertEqual(loader.get_netid_changed_count(), 1)
            self.assertEqual(loader.get_updated_count(), 1)
            self.assertTrue(loader.has_error())
