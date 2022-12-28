# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TransactionTestCase
from sis_provisioner.models import UwAccount, get_now
from sis_provisioner.dao.pws import get_person
from sis_provisioner.dao.uw_account import (
    delete_uw_account, get_all_uw_accounts, get_by_bridgeid,
    get_by_employee_id, get_by_netid, save_uw_account)
from sis_provisioner.tests import fdao_pws_override
from sis_provisioner.tests.account_managers import set_db_records


@fdao_pws_override
class TestUwAccountDao(TransactionTestCase):

    def mock_uw_account(self, uwnetid):
        return UwAccount.objects.create(netid=uwnetid,
                                        last_updated=get_now())

    def test_get_all_uw_accounts(self):
        self.assertEqual(len(get_all_uw_accounts()), 0)

        user1 = self.mock_uw_account('staff')
        user2 = self.mock_uw_account('faculty')

        users = get_all_uw_accounts()
        self.assertEqual(len(users), 2)

    def test_get_by_ids(self):
        set_db_records()
        self.assertIsNone(get_by_bridgeid(201))
        self.assertEqual(get_by_bridgeid(196).netid, 'staff')
        self.assertEqual(get_by_employee_id("123456789").netid, "javerage")

        # multiple records
        self.assertIsNone(get_by_employee_id("000000006"))

        self.assertEqual(get_by_netid('staff').bridge_id, 196)

        delete_uw_account('staff')
        self.assertIsNone(get_by_netid('staff'))
        self.assertIsNone(get_by_bridgeid(0))
        self.assertIsNone(get_by_employee_id(None))
        self.assertIsNone(get_by_netid('none'))

    def test_save_new_uw_account(self):
        affiemp = person = get_person('affiemp')
        acc = save_uw_account(affiemp)
        self.assertEqual(acc.netid, 'affiemp')
        self.assertFalse(acc.has_prev_netid())
        self.assertEqual(len(get_all_uw_accounts()), 1)

    def test_save_uw_account(self):
        acc1 = self.mock_uw_account('tyler')
        self.assertEqual(len(get_all_uw_accounts()), 1)

        person = get_person('faculty')
        acc = save_uw_account(person)
        self.assertEqual(acc.netid, person.uwnetid)
        self.assertTrue(acc.has_prev_netid())
        self.assertEqual(acc.prev_netid, 'tyler')
        self.assertEqual(len(get_all_uw_accounts()), 1)

    def test_save_uw_accounts(self):
        # test a user with multiple accounts
        acc1 = self.mock_uw_account('ellen')
        acc2 = self.mock_uw_account('retiree')
        self.assertEqual(len(get_all_uw_accounts()), 2)
        person = get_person('retiree')
        acc = save_uw_account(person)
        self.assertEqual(acc.netid, person.uwnetid)
        self.assertEqual(acc.prev_netid, 'ellen')
        self.assertEqual(len(get_all_uw_accounts()), 1)
