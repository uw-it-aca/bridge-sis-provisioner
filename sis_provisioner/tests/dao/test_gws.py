from django.test import TestCase
from sis_provisioner.dao import DataFailureException
from sis_provisioner.dao.gws import (
    get_members_of_group, get_potential_users)
from sis_provisioner.tests import fdao_gws_override


@fdao_gws_override
class TestGwsDao(TestCase):

    def test_get_affiliate(self):
        self.assertRaises(DataFailureException, get_members_of_group, "uw")

    def test_get_potential_users(self):
        user_set = get_potential_users()
        self.assertEqual(len(user_set), 6)
        self.assertTrue("retiree" in user_set)
        self.assertTrue("affiemp" in user_set)
        self.assertTrue("faculty" in user_set)
        self.assertTrue("javerage" in user_set)
        self.assertTrue("not_in_pws" in user_set)
        self.assertTrue("staff" in user_set)