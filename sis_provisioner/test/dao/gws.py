from restclients.exceptions import DataFailureException
from django.test import TestCase
from sis_provisioner.test import FGWS
from sis_provisioner.dao.gws import get_uw_members, is_uw_member


class TestGwsDao(TestCase):

    def test_get_uw_members(self):
        with self.settings(RESTCLIENTS_GWS_DAO_CLASS=FGWS):
            users = get_uw_members()
            self.assertIsNotNone(users)
            self.assertEqual(len(users), 11)

            self.assertEqual(users[0], "botgrad")
            self.assertEqual(users[1], "faculty")
            self.assertEqual(users[2], "javerage")
            self.assertEqual(users[3], "seagrad")
            self.assertEqual(users[4], "staff")
            self.assertEqual(users[5], "supple")
            self.assertEqual(users[6], "tacgrad")
            self.assertEqual(users[7], "renamed")
            self.assertEqual(users[8], "none")
            self.assertEqual(users[9], "retiree")
            self.assertEqual(users[10], "leftuw")

    def test_is_uw_member(self):
        with self.settings(RESTCLIENTS_GWS_DAO_CLASS=FGWS):
            self.assertTrue(is_uw_member("javerage"))
            self.assertFalse(is_uw_member("none"))
            self.assertFalse(is_uw_member("leftuw"))
