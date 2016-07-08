from django.conf import settings
from django.test import TransactionTestCase
from django.test.utils import override_settings
from restclients.exceptions import DataFailureException
from sis_provisioner.test import FGWS, FPWS
from sis_provisioner.load_users import LoadUsers


class TestLoadUsers(TransactionTestCase):

    def test_get_uw_members(self):
        with self.settings(RESTCLIENTS_GWS_DAO_CLASS=FGWS,
                           RESTCLIENTS_PWS_DAO_CLASS=FPWS):
            load_users = LoadUsers()
            load_users.fetch_all()

            self.assertEqual(load_users.get_total_count(), 7)
            self.assertEqual(load_users.get_invalid_count(), 1)
