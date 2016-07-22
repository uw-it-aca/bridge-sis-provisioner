from django.conf import settings
from django.test import TransactionTestCase
from django.test.utils import override_settings
from restclients.exceptions import DataFailureException
from sis_provisioner.test import FGWS, FPWS, FHRP
from sis_provisioner.user_loader import UserLoader


class TestLoadUsers(TransactionTestCase):

    def test_load_users_no_hrp(self):
        with self.settings(RESTCLIENTS_GWS_DAO_CLASS=FGWS,
                           RESTCLIENTS_PWS_DAO_CLASS=FPWS):
            load_users = UserLoader(include_hrp=False)
            load_users.fetch_all()
            self.assertEqual(load_users.get_total_count(), 11)
            self.assertEqual(load_users.get_add_count(), 8)
            self.assertEqual(load_users.get_delete_count(), 0)
            self.assertEqual(load_users.get_netid_changed_count(), 0)
            self.assertEqual(load_users.get_regid_changed_count(), 0)
            self.assertEqual(len(load_users.get_users_to_add()), 8)
            self.assertEqual(len(load_users.get_users_to_delete()), 0)
            self.assertEqual(len(load_users.get_users_netid_changed()), 0)
            self.assertEqual(len(load_users.get_users_regid_changed()), 0)
            self.assertFalse(load_users.include_hrp())
            # reload should find no changed user to add
            load_users.fetch_all()
            self.assertEqual(load_users.get_total_count(), 11)
            self.assertEqual(load_users.get_add_count(), 0)

    def test_load_users_with_hrp(self):
        with self.settings(RESTCLIENTS_GWS_DAO_CLASS=FGWS,
                           RESTCLIENTS_PWS_DAO_CLASS=FPWS,
                           RESTCLIENTS_HRPWS_DAO_CLASS=FHRP):
            load_users = UserLoader(include_hrp=True)
            load_users.fetch_all()
            self.assertEqual(load_users.get_total_count(), 11)
            self.assertEqual(load_users.get_add_count(), 8)
            self.assertEqual(load_users.get_delete_count(), 0)
            self.assertEqual(load_users.get_netid_changed_count(), 0)
            self.assertEqual(load_users.get_regid_changed_count(), 0)
            self.assertEqual(len(load_users.get_users_to_add()), 8)
            self.assertTrue(load_users.include_hrp())
            # reload should find no changed user to add
            load_users.fetch_all()
            self.assertEqual(load_users.get_total_count(), 11)
            self.assertEqual(load_users.get_add_count(), 0)
