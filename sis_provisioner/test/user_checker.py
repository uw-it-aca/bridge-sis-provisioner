from django.conf import settings
from django.test import TransactionTestCase
from datetime import timedelta
from django.utils import timezone
from sis_provisioner.test import FGWS, FPWS, set_pass_terminate_date
from sis_provisioner.models import BridgeUser, get_now
from sis_provisioner.user_checker import mark_terminated_users,\
    delete_terminated_users
from sis_provisioner.user_loader import UserLoader, PurgeUserLoader


class TestUserChecker(TransactionTestCase):

    def test_mark_terminated_users(self):
        with self.settings(RESTCLIENTS_PWS_DAO_CLASS=FPWS):
            load_users = UserLoader(include_hrp=False)
            load_users.fetch_all()
            self.assertEqual(load_users.get_total_count(), 11)
            self.assertEqual(load_users.get_add_count(), 8)

            total_users, users_nolonger_user_uw = mark_terminated_users()
            self.assertEqual(total_users, 8)
            self.assertEqual(len(users_nolonger_user_uw), 2)
            for netid in users_nolonger_user_uw:
                set_pass_terminate_date(netid)

            d_loader = PurgeUserLoader()
            d_loader.fetch_all()
            self.assertEqual(d_loader.get_total_count(), 8)
            self.assertEqual(d_loader.get_delete_count(), 2)
            users_deleted = d_loader.get_users_to_delete()
            self.assertEqual(users_deleted[0], "retiree")
            self.assertEqual(users_deleted[1], "leftuw")

    def delete_terminated_users(self, uwnetid):
        with self.settings(RESTCLIENTS_PWS_DAO_CLASS=FPWS):
            load_users = UserLoader(include_hrp=False)
            load_users.fetch_all()
            self.assertEqual(load_users.get_total_count(), 11)
            self.assertEqual(load_users.get_add_count(), 8)
            total_users, users_nolonger_user_uw = mark_terminated_users()

            for netid in users_nolonger_user_uw:
                set_pass_terminate_date(netid)

            total_users, users_deleted = delete_terminated_users()
            self.assertEqual(total_users, 8)
            self.assertEqual(len(users_deleted), 2)
            self.assertEqual(users_deleted[0], "retiree")
            self.assertEqual(users_deleted[1], "leftuw")
