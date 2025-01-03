# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import time
from django.test import TransactionTestCase
from django.core.management import call_command
from sis_provisioner.dao.uw_account import get_by_netid
from sis_provisioner.tests import fdao_pws_override
from sis_provisioner.tests.account_managers import set_db_records


@fdao_pws_override
class TestDisableUser(TransactionTestCase):

    def test_disable_user(self):
        set_db_records()

        # existing user
        call_command('disable_user', "retiree")
        uw_acc = get_by_netid("retiree")
        self.assertTrue(uw_acc.disabled)
        # error when deleting
        call_command('disable_user', "ellen")

        # changed uwnetid
        call_command('disable_user', "faculty")

        # already disabled
        call_command('disable_user', "staff")
