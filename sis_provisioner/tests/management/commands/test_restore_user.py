# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import time
from django.test import TransactionTestCase
from django.core.management import call_command
from sis_provisioner.dao.uw_account import get_by_netid
from sis_provisioner.management.commands.restore_user import get_bridge_account
from sis_provisioner.tests import fdao_pws_override
from sis_provisioner.tests.account_managers import set_uw_account


@fdao_pws_override
class TestRestoreUser(TransactionTestCase):

    def test_restore_user(self):
        staff = set_uw_account("staff")
        staff.set_disable()
        staff.set_ids(196, "100000001")

        call_command('restore_user', "staff")
        uw_acc = get_by_netid("staff")
        self.assertFalse(uw_acc.disabled)

        # no longer disabled
        call_command('restore_user', "staff")

    def test_restore_user_changed_uwnetid(self):
        tyler = set_uw_account("tyler")
        tyler.set_disable()
        bacc = get_bridge_account(tyler)
        print(bacc)
        call_command('restore_user', "tyler")
        uw_acc = get_by_netid("faculty")
        self.assertFalse(uw_acc.disabled)
