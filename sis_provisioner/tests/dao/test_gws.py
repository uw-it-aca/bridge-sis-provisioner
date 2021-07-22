from django.test import TestCase
from unittest.mock import patch
from freezegun import freeze_time
from uw_gws.models import GroupHistory
from sis_provisioner.dao import (
    DataFailureException, read_gws_cache_file, write_gws_cache_file)
from sis_provisioner.dao.gws import (
    get_members_of_group, get_potential_users, get_bridge_authors,
    get_additional_users, _get_member_changes, _get_start_timestamp,
    get_changed_members, get_added_members, get_deleted_members)
from sis_provisioner.tests import fdao_gws_override


@fdao_gws_override
class TestGwsDao(TestCase):

    def test_get_affiliate(self):
        self.assertRaises(DataFailureException, get_members_of_group, "uw")

    def test_get_potential_users(self):
        user_set = get_potential_users()
        self.assertEqual(len(user_set), 7)
        self.assertTrue("retiree" in user_set)
        self.assertTrue("affiemp" in user_set)
        self.assertTrue("faculty" in user_set)
        self.assertTrue("javerage" in user_set)
        self.assertTrue("not_in_pws" in user_set)
        self.assertTrue("error500" in user_set)
        self.assertTrue("staff" in user_set)

    def test_get_additional_users(self):
        user_set = get_additional_users()
        self.assertEqual(len(user_set), 1)
        self.assertTrue("not_in_pws" in user_set)

    def test_get_bridge_authors(self):
        user_set = get_bridge_authors()
        self.assertEqual(len(user_set), 5)
        self.assertTrue("alumni" in user_set)
        self.assertTrue("javerage" in user_set)
        self.assertTrue("staff" in user_set)
        self.assertTrue("error500" in user_set)
        self.assertTrue("not_in_pws" in user_set)

    def test_get_member_changes(self):
        changes = _get_member_changes("uw_member", 1626215400)
        self.assertEqual(len(changes), 3)
        self.assertEqual(changes[2].member_uwnetid, "added")
        self.assertTrue(changes[2].is_add_member)
        self.assertEqual(changes[1].member_uwnetid, "retiree")
        self.assertTrue(changes[1].is_delete_member)
        self.assertEqual(changes[0].member_uwnetid, "leftuw")
        self.assertTrue(changes[0].is_delete_member)

    @freeze_time("2021-07-20 18:30:00", tz_offset=-7)
    def test_get_start_timestamp(self):
        ts = _get_start_timestamp(60)
        self.assertEqual(ts, 1626777000)

    @patch('sis_provisioner.dao.gws._get_start_timestamp',
           return_value=1626215400, spec=True)
    def test_get_changed_members(self, mock_fn):
        users_added, users_deleted = get_changed_members('uw_member', 12)
        self.assertEqual(len(users_added), 1)
        self.assertTrue("added" in users_added)
        self.assertEqual(len(users_deleted), 2)
        self.assertTrue("retiree" in users_deleted)
        self.assertTrue("leftuw" in users_deleted)

        users_added, users_deleted = get_changed_members('uw_affiliate', 7)
        self.assertEqual(len(users_added), 0)
        self.assertEqual(len(users_deleted), 0)

    @patch('sis_provisioner.dao.gws._get_start_timestamp',
           return_value=1626215400, spec=True)
    def test_get_added_members(self, mock_fn):
        netid_set = get_added_members(12)
        self.assertEqual(len(netid_set), 1)
        self.assertTrue("added" in netid_set)

    @patch('sis_provisioner.dao.gws._get_start_timestamp',
           return_value=1626215400, spec=True)
    def test_get_deleted_members(self, mock_fn):
        netid_set = get_deleted_members(7)
        self.assertEqual(len(netid_set), 2)
        self.assertTrue("retiree" in netid_set)
        self.assertTrue("leftuw" in netid_set)
