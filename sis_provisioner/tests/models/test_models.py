# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import json
from django.test import TransactionTestCase
from datetime import timedelta, datetime
from sis_provisioner.models import (
    UwAccount, get_now, datetime_to_str, GRACE_PERIOD)


class TestModels(TransactionTestCase):

    def mock_uw_account(self, uwnetid):
        return UwAccount.objects.create(netid=uwnetid,
                                        last_updated=get_now())

    def test_uw_account(self):
        user = self.mock_uw_account('staff')
        self.assertFalse(user.has_terminate_date())

        user.set_ids(0, None)
        self.assertFalse(user.has_bridge_id())
        self.assertFalse(user.has_employee_id())

        self.assertFalse(user.has_bridge_id())
        user.set_ids(123, "100000005")
        self.assertTrue(user.has_bridge_id())
        self.assertEqual(user.bridge_id, 123)
        self.assertTrue(user.has_employee_id())
        self.assertEqual(user.employee_id, "100000005")

        qset = UwAccount.objects.filter(employee_id="100000005")
        self.assertEqual(len(qset), 1)
        self.assertEqual(qset[0].employee_id, "100000005")

        user.set_terminate_date()
        self.assertTrue(user.has_terminate_date())
        self.assertFalse(user.passed_terminate_date())
        date1 = user.terminate_at
        user.set_terminate_date()
        self.assertEqual(user.terminate_at, date1)

        user.terminate_at -= timedelta(days=GRACE_PERIOD + 1)
        self.assertTrue(user.passed_terminate_date())

        user.set_terminate_date(graceful=False)
        dtime = user.terminate_at
        self.assertTrue(get_now() < (dtime + timedelta(seconds=3)))

        user.prev_netid = 'staff0'
        self.assertTrue(user.has_prev_netid())
        self.assertTrue(user.netid_changed())
        user.prev_netid = None
        self.assertFalse(user.has_prev_netid())

        user.set_disable()
        self.assertTrue(user.disabled)
        user.set_restored()
        self.assertFalse(user.disabled)

        user.set_disable()
        user.set_terminate_date(graceful=False)
        user.prev_netid = 'staff0'

        user.set_updated()
        self.assertFalse(user.disabled)
        self.assertFalse(user.has_terminate_date())
        self.assertFalse(user.has_prev_netid())

        self.assertIsNotNone(user.json_data())
        self.assertIsNotNone(str(user))

    def test_datetime_to_str(self):
        dt = datetime(2017, 12, 5, 15, 3, 1)
        self.assertEqual(datetime_to_str(dt), "2017-12-05T15:03:01")
        self.assertIsNone(datetime_to_str(None))

    def test_class_method(self):
        uw_acc1 = self.mock_uw_account("tyler")
        self.assertTrue(UwAccount.exists("tyler"))

        user = UwAccount.get("tyler")
        self.assertTrue(user == uw_acc1)

        uw_acc = UwAccount.get_uw_acc("faculty", ["tyler"])
        self.assertEqual(uw_acc.netid, "faculty")
        self.assertEqual(uw_acc.prev_netid, "tyler")

        uw_acc1 = UwAccount.get_uw_acc("staff", [], create=True)
        self.assertEqual(uw_acc1.netid, "staff")
        self.assertFalse(uw_acc == uw_acc1)

        uw_acc2 = UwAccount.get_uw_acc("staff", [])
        self.assertTrue(uw_acc1 == uw_acc2)
