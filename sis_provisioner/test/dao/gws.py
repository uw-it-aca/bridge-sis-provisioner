from restclients.exceptions import DataFailureException
from sis_provisioner.test import FGWS
from sis_provisioner.test.dao import TestDao
from sis_provisioner.dao.gws import get_uw_members


class TestGwsDao(TestDao):

    def test_get_uw_members(self):
        with self.settings(RESTCLIENTS_GWS_DAO_CLASS=FGWS):
            users = get_uw_members()
            self.assertIsNotNone(users)
            self.assertEqual(len(users), 7)

            self.assertEqual(users[0], "botgrad")
            self.assertEqual(users[1], "faculty")
            self.assertEqual(users[2], "javerage")
            self.assertEqual(users[3], "seagrad")
            self.assertEqual(users[4], "staff")
            self.assertEqual(users[5], "supple")
            self.assertEqual(users[6], "tacgrad")
