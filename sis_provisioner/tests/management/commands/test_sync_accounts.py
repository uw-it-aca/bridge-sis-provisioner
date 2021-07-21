# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import time
from django.test import TransactionTestCase
from django.core.management import call_command
from sis_provisioner.tests import (
    fdao_gws_override, fdao_pws_override, fdao_bridge_override)
from sis_provisioner.tests.account_managers import set_db_records


@fdao_gws_override
@fdao_pws_override
@fdao_bridge_override
class TestLoadUserViaBridgeApi(TransactionTestCase):

    def test_load_from_gws_to_bridge(self):
        with self.settings(BRIDGE_GWS_CACHE='/tmp/gwsusermc'):
            set_db_records()
            call_command('sync_accounts', 'gws')

    def test_load_from_dbemp_to_bridge(self):
        time.sleep(1)
        set_db_records()
        call_command('sync_accounts', 'db-emp')

    def test_load_from_dbother_to_bridge(self):
        time.sleep(1)
        set_db_records()
        call_command('sync_accounts', 'db-other')

    def test_load_bridge_to_db(self):
        time.sleep(2)
        set_db_records()
        call_command('sync_accounts', 'bridge')

    def test_load_pws_bridge(self):
        time.sleep(2)
        set_db_records()
        call_command('sync_accounts', 'pws')

    def test_load_hrp_bridge(self):
        time.sleep(2)
        set_db_records()
        call_command('sync_accounts', 'hrp')
