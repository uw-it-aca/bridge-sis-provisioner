# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TransactionTestCase
from freezegun import freeze_time
from sis_provisioner.dao.hrp import get_worker_updates
from sis_provisioner.account_managers.bridge_worker import BridgeWorker
from sis_provisioner.account_managers.hrp_bridge import HrpBridgeLoader
from sis_provisioner.tests import (
    fdao_hrp_override, fdao_pws_override,
    fdao_gws_override, fdao_bridge_override)
from sis_provisioner.tests.account_managers import set_db_records


@fdao_bridge_override
@fdao_hrp_override
@fdao_gws_override
@fdao_pws_override
class TestHrpBridgeLoader(TransactionTestCase):

    @freeze_time("2019-09-01 10:30:00")
    def test_load_hrp(self):
        with self.settings(ERRORS_TO_ABORT_LOADER=[],
                           BRIDGE_WORKER_CHANGE_WINDOW=30):
            set_db_records()
            loader = HrpBridgeLoader(BridgeWorker())
            loader.users_to_process = loader.fetch_users()
            loader.process_users()
            self.assertEqual(loader.get_total_count(), 2)
            self.assertEqual(loader.get_total_checked_users(), 1)
            self.assertEqual(loader.get_new_user_count(), 0)
            self.assertEqual(loader.get_restored_count(), 0)
            self.assertEqual(loader.get_netid_changed_count(), 1)
            self.assertEqual(loader.get_updated_count(), 1)
            self.assertFalse(loader.has_error())
