# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TransactionTestCase
from django.core.management import call_command
from sis_provisioner.tests import (
    fdao_gws_override, fdao_pws_override, fdao_bridge_override)
from sis_provisioner.tests.account_managers import (
    set_db_records, set_db_err_records)


@fdao_bridge_override
@fdao_gws_override
@fdao_pws_override
class TestLoadUserViaBridgeApi(TransactionTestCase):

    def test_load_from_gws_to_bridge(self):
        set_db_records()
        set_db_err_records()
        call_command('sync_authors', '-n')
        call_command('sync_authors')
