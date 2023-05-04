# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import time
from django.test import TransactionTestCase
from django.core.management import call_command
from sis_provisioner.tests import fdao_pws_override
from sis_provisioner.tests.account_managers import set_db_records


@fdao_pws_override
class TestLoadUserViaBridgeApi(TransactionTestCase):

    def test_load_from_gws_to_bridge(self):
        set_db_records()
        call_command('sync_eid', '-n')
        call_command('sync_eid')
