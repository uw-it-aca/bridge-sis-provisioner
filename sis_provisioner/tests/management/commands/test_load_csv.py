# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import time
from django.test import TransactionTestCase
from django.conf import settings
from django.core.management import call_command
from sis_provisioner.tests.csv import (
    set_db_records, fdao_pws_override, fdao_hrp_override)

CSV_ROOT = "/tmp/fl_test"


@fdao_pws_override
@fdao_hrp_override
class TestLoadUserViaBridgeApi(TransactionTestCase):

    def test_load_from_gws_to_bridge(self):
        with self.settings(BRIDGE_IMPORT_USER_FILE_SIZE=2,
                           BRIDGE_IMPORT_CSV_ROOT=CSV_ROOT):
            set_db_records()
            call_command('load_csv')
