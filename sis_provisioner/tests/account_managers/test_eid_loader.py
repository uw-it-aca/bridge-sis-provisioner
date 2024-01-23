# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging
from datetime import timedelta
from django.test import TransactionTestCase
from sis_provisioner.dao.uw_account import get_by_employee_id
from sis_provisioner.account_managers.eid_loader import load
from sis_provisioner.tests import fdao_pws_override
from sis_provisioner.tests.account_managers import set_uw_account


@fdao_pws_override
class TestEidLoader(TransactionTestCase):

    def test_load(self):
        set_uw_account("javerage")
        set_uw_account("staff")
        set_uw_account("tyler")
        self.assertEqual(load(),
                         "Updated employee_ids for 3 out of 3 users")
        self.assertEqual(get_by_employee_id("123456789").netid, "javerage")
        self.assertEqual(get_by_employee_id("100000001").netid, "staff")
        self.assertEqual(get_by_employee_id("000000005").netid, "tyler")
