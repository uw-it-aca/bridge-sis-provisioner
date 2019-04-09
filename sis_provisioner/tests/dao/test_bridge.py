from django.test import TransactionTestCase
from restclients_core.exceptions import DataFailureException
from uw_bridge.custom_field import new_regid_custom_field
from uw_bridge.models import BridgeUser
from sis_provisioner.models import UwAccount, get_now
from sis_provisioner.dao import DataFailureException
from sis_provisioner.dao.bridge import (
    add_bridge_user, change_uwnetid, delete_bridge_user, get_all_bridge_users,
    get_user_by_bridgeid, get_user_by_uwnetid, restore_bridge_user,
    update_bridge_user, get_regid_from_bridge_user)
from sis_provisioner.tests import fdao_bridge_override
from sis_provisioner.tests.dao import get_mock_bridge_user


@fdao_bridge_override
class TestBridgeDao(TransactionTestCase):

    def test_get_all_bridge_users(self):
        busers = get_all_bridge_users()
        self.assertEqual(len(busers), 6)
        buser = busers[0]
        self.assertEqual(buser.bridge_id, 194)
        self.assertEqual(buser.netid, 'ellen')
        buser = busers[1]
        self.assertEqual(buser.bridge_id, 195)
        self.assertEqual(buser.netid, 'javerage')
        buser = busers[2]
        self.assertEqual(buser.bridge_id, 198)
        self.assertEqual(buser.netid, 'tyler')
        buser = busers[3]
        self.assertEqual(buser.bridge_id, 199)
        self.assertEqual(buser.netid, 'alumni')
        buser = busers[4]
        self.assertEqual(buser.bridge_id, 200)
        self.assertEqual(buser.netid, 'leftuw')
        buser = busers[5]
        self.assertEqual(buser.bridge_id, 204)
        self.assertEqual(buser.netid, 'retiree')

    def test_add_bridge_user(self):
        # not exist
        user = get_mock_bridge_user(0,
                                    'affiemp',
                                    "affiemp@uw.edu",
                                    "Alena Affi",
                                    "Alena",
                                    "Affi",
                                    "10000000000000000000000000000011")
        # normal case
        ret_user = add_bridge_user(user)
        self.assertEqual(ret_user.netid, 'affiemp')
        self.assertEqual(ret_user.bridge_id, 201)
        self.assertEqual(ret_user.full_name, "Alena Affi")

    def test_delete_bridge_user(self):
        # normal case
        user = get_mock_bridge_user(0,
                                    'leftuw',
                                    "leftuw@uw.edu",
                                    "Who LEFT",
                                    "WHO",
                                    "LEFT",
                                    "10000000000000000000000000000FFF")
        self.assertRaises(DataFailureException, delete_bridge_user, user)
        user.bridge_id = 200
        self.assertTrue(delete_bridge_user(user))

    def test_change_uwnetid(self):
        exists, buser = get_user_by_bridgeid(198)
        self.assertTrue(exists)
        self.assertEqual(buser.netid, 'tyler')

        uw_acc = UwAccount(netid='faculty',
                           bridge_id=198,
                           prev_netid='tyler',
                           last_updated=get_now())
        bridge_user = change_uwnetid(uw_acc)
        self.assertEqual(bridge_user.netid, 'faculty')

        self.assertRaises(DataFailureException,
                          change_uwnetid,
                          UwAccount(netid='none',
                                    bridge_id=300,
                                    last_updated=get_now()))

    def test_get_bridge_user(self):
        self.assertRaises(DataFailureException,
                          get_user_by_uwnetid,
                          "error500")

        exists, buser = get_user_by_uwnetid("none")
        self.assertFalse(exists)

        # terminated
        exists, buser = get_user_by_uwnetid("staff")
        self.assertTrue(exists)
        self.assertIsNone(buser)

        exists, buser = get_user_by_uwnetid("javerage")
        self.assertTrue(exists)
        self.assertIsNotNone(buser)
        self.assertEqual(buser.bridge_id, 195)
        self.assertEqual(buser.netid, "javerage")
        self.assertEqual(buser.full_name, "Average Joseph Student")
        self.assertEqual(len(buser.custom_fields), 1)
        self.assertEqual(buser.custom_fields[0].value_id, '3')
        self.assertEqual(buser.custom_fields[0].field_id, '5')
        self.assertEqual(buser.custom_fields[0].value,
                         "9136CCB8F66711D5BE060004AC494FFE")

        exists, buser = get_user_by_bridgeid(204)
        self.assertTrue(exists)
        self.assertIsNotNone(buser)
        self.assertEqual(buser.bridge_id, 204)
        self.assertEqual(buser.netid, 'retiree')
        self.assertEqual(buser.email, 'retiree@uw.edu')
        self.assertEqual(get_regid_from_bridge_user(buser),
                         "10000000000000000000000000000066")

        exists, buser = get_user_by_bridgeid(300)
        self.assertFalse(exists)

    def test_restore_bridge_user(self):
        uw_acc = UwAccount(netid='staff',
                           bridge_id=196,
                           last_updated=get_now())
        buser = restore_bridge_user(uw_acc)
        self.assertEqual(buser.netid, 'staff')

        self.assertRaises(DataFailureException,
                          restore_bridge_user,
                          UwAccount(netid='none',
                                    bridge_id=300,
                                    last_updated=get_now()))

    def test_update_user(self):
        user = get_mock_bridge_user(198,
                                    'faculty',
                                    'faculty@uw.edu',
                                    'William E Faculty',
                                    "William E",
                                    "Faculty",
                                    "10000000000000000000000000000005")
        ret_user = update_bridge_user(user)
        self.assertEqual(ret_user.netid, "faculty")

        user = get_mock_bridge_user(300,
                                    'none',
                                    "none@uw.edu",
                                    "No Name",
                                    "No",
                                    "Name",
                                    "10000000000000000000000000000000")
        self.assertRaises(DataFailureException, update_bridge_user, user)
