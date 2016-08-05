from django.conf import settings
from django.test import TransactionTestCase
from datetime import timedelta
from django.utils import timezone
from sis_provisioner.test import FGWS, FPWS, set_pass_terminate_date
from sis_provisioner.models import BridgeUser, get_now
from sis_provisioner.user_checker import PurgeUserLoader
from sis_provisioner.user_loader import UserLoader


class TestPurgeUserLoader(TransactionTestCase):

    def test_purge_user(self):
        with self.settings(RESTCLIENTS_PWS_DAO_CLASS=FPWS):
            load_users = UserLoader(include_hrp=False)
            load_users.fetch_all()
            self.assertEqual(load_users.get_total_count(), 11)
            self.assertEqual(load_users.get_add_count(), 8)

            d_loader = PurgeUserLoader()
            d_loader.fetch_all()
            self.assertEqual(d_loader.get_total_count(), 8)
            self.assertEqual(d_loader.get_users_left_uw_count(), 1)
            self.assertEqual(d_loader.get_delete_count(), 1)
            users_left_uw = d_loader.get_users_to_delete()
            self.assertEqual(users_left_uw[0], "retiree")
            users_left_uw = d_loader.get_users_left_uw()
            self.assertEqual(users_left_uw[0], "leftuw")
            # change terminate_date
            user2 = BridgeUser.objects.get(netid='leftuw')
            user2.save_terminate_date(graceful=False)

            d_loader.fetch_all()
            self.assertEqual(d_loader.get_total_count(), 7)
            self.assertEqual(d_loader.get_users_left_uw_count(), 1)
            self.assertEqual(d_loader.get_delete_count(), 1)
            users_deleted = d_loader.get_users_to_delete()
            self.assertEqual(users_deleted[0], "leftuw")
