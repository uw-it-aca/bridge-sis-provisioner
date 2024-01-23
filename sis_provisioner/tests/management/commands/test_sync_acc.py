# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TransactionTestCase
from django.core.management import call_command
from sis_provisioner.tests import fdao_pws_override
from sis_provisioner.tests.account_managers import set_uw_account


@fdao_pws_override
class TestRestoreUser(TransactionTestCase):

    def test_sync_user(self):
        staff = set_uw_account("staff")
        staff.set_ids(196, "100000001")
        javerage = set_uw_account("javerage")
        call_command('sync_acc', 'javerage')

        staff = set_uw_account("alumni")
        call_command('sync_acc', "alumni")
