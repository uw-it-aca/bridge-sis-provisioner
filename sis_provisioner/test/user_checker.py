from django.conf import settings
from django.test import TransactionTestCase
from sis_provisioner.test import FGWS, FPWS
from sis_provisioner.user_checker import mark_terminated_users
from sis_provisioner.user_loader import UserLoader


class TestUserChecker(TransactionTestCase):

    def test_mark_terminated_users(self):
        with self.settings(RESTCLIENTS_PWS_DAO_CLASS=FPWS):
            users_nolonger_user_uw = mark_terminated_users()
            self.assertEqual(len(users_nolonger_user_uw), 0)
