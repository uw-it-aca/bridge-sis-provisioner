import json
from django.test import TransactionTestCase
from datetime import timedelta, datetime
from sis_provisioner.models import (
    UwAccount, get_now, datetime_to_str, GRACE_PERIOD)


class TestModels(TransactionTestCase):

    def mock_uw_account(self, uwnetid):
        return UwAccount.objects.create(netid=uwnetid,
                                        last_updated=get_now())

    def test_uw_bridge_user(self):
        user = self.mock_uw_account('staff')
        self.assertFalse(user.has_terminate_date())

        self.assertFalse(user.has_bridge_id())
        user.set_bridge_id(123)
        self.assertTrue(user.has_bridge_id())
        self.assertEqual(user.bridge_id, 123)

        user.set_terminate_date()
        self.assertTrue(user.has_terminate_date())
        self.assertFalse(user.passed_terminate_date())

        user.terminate_at -= timedelta(days=GRACE_PERIOD + 1)
        self.assertTrue(user.passed_terminate_date())

        user.set_terminate_date(graceful=False)
        dtime = user.terminate_at
        self.assertTrue(get_now() < (dtime + timedelta(seconds=3)))

        user.clear_terminate_date()
        self.assertFalse(user.has_terminate_date())

        user.prev_netid = 'staff0'
        self.assertTrue(user.has_prev_netid())
        self.assertTrue(user.netid_changed())
        user.clear_prev_netid()
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
        self.assertEqual(datetime_to_str(dt), "2017-12-05 15:03:01")
        self.assertIsNone(datetime_to_str(None))

    def test_class_method(self):
        user1 = self.mock_uw_account("tyler")
        self.assertTrue(UwAccount.exists("tyler"))

        user = UwAccount.get("tyler")
        self.assertEqual(user, user1)

        uw_acc = UwAccount.get_uw_acc("faculty", ["tyler"])
        self.assertEqual(uw_acc.netid, "faculty")
        self.assertEqual(uw_acc.prev_netid, "tyler")

        uw_acc1 = UwAccount.get_uw_acc("staff", [], create=True)
        self.assertEqual(uw_acc1.netid, "staff")

        uw_acc2 = UwAccount.get_uw_acc("staff", [])
        self.assertEqual(uw_acc1, uw_acc2)