from django.test import TestCase
from restclients.exceptions import DataFailureException
from sis_provisioner.test import fdao_gws_override
from sis_provisioner.dao.gws import get_uw_members, is_uw_member,\
    get_affiliate_employees, get_potential_users, is_qualified_user,\
    is_affiliate_employee


@fdao_gws_override
class TestGwsDao(TestCase):

    def test_get_uw_members(self):
        users = get_uw_members()
        self.assertIsNotNone(users)
        self.assertEqual(len(users), 10)

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

    def test_get_affiliate_employees(self):
        users = get_affiliate_employees()
        self.assertIsNotNone(users)
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0], "affiemp")

    def test_get_potential_users(self):
        users = get_potential_users()
        self.assertIsNotNone(users)
        self.assertEqual(len(users), 11)

    def test_is_uw_member(self):
        self.assertTrue(is_uw_member("javerage"))
        self.assertTrue(is_uw_member("none"))
        self.assertFalse(is_uw_member("leftuw"))
        self.assertFalse(is_uw_member("bridge"))

    def test_is_affiliate_employee(self):
        self.assertTrue(is_affiliate_employee("affiemp"))
        self.assertFalse(is_affiliate_employee("javerage"))
        self.assertFalse(is_uw_member("bridge"))

    def test_is_qualified_user(self):
        self.assertTrue(is_qualified_user("javerage"))
        self.assertTrue(is_qualified_user("affiemp"))
        self.assertFalse(is_uw_member("leftuw"))
        self.assertFalse(is_qualified_user("bridge"))
