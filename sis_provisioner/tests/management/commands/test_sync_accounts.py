# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import time
from django.test import TransactionTestCase
from unittest.mock import patch
from freezegun import freeze_time
from django.core.management import call_command
from sis_provisioner.account_managers.gws_bridge import GwsBridgeLoader
from sis_provisioner.tests.account_managers import set_db_records


users = ['affiemp', 'error500', 'faculty', 'javerage',
         'not_in_pws', 'retiree', 'staff']


class TestLoadUserViaBridgeApi(TransactionTestCase):

    @patch.object(GwsBridgeLoader, 'fetch_users',
                  return_value=users, spec=True)
    def test_load_from_gws_to_bridge(self, mock_fn):
        with self.settings(BRIDGE_GWS_CACHE='/tmp/gwsusermc'):
            set_db_records()
            call_command('sync_accounts', 'gws')

    def test_load_from_customg_to_bridge(self):
        time.sleep(1)
        set_db_records()
        call_command('sync_accounts', 'customg')

    def test_load_from_dbacc_to_bridge(self):
        time.sleep(1)
        set_db_records()
        call_command('sync_accounts', 'db-acc')

    def test_load_from_delete_to_bridge(self):
        time.sleep(1)
        set_db_records()
        call_command('sync_accounts', 'delete')

    def test_load_bridge_to_db(self):
        time.sleep(2)
        set_db_records()
        call_command('sync_accounts', 'bridge')

    @freeze_time("2019-09-01 20:30:00")
    def test_load_pws_bridge(self):
        time.sleep(2)
        set_db_records()
        call_command('sync_accounts', 'pws')

    @freeze_time("2019-09-01 10:30:00")
    def test_load_hrp_bridge(self):
        with self.settings(BRIDGE_WORKER_CHANGE_WINDOW=30):
            time.sleep(2)
            set_db_records()
            call_command('sync_accounts', 'hrp')
