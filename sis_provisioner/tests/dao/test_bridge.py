from django.test import TransactionTestCase
from restclients_core.exceptions import DataFailureException
from uw_bridge.models import BridgeUser
from sis_provisioner.models import UwAccount, get_now
from sis_provisioner.dao import DataFailureException
from sis_provisioner.dao.bridge import BridgeUsers
from sis_provisioner.tests import fdao_bridge_override
from sis_provisioner.tests.dao import get_mock_bridge_user


@fdao_bridge_override
class TestBridge(TransactionTestCase):

    @classmethod
    def setUpClass(cls):
        TestBridge.bridge = BridgeUsers()

    def test_get_all_bridge_users(self):
        busers = TestBridge.bridge.get_all_users()
        self.assertEqual(len(busers), 8)
        buser = busers[0]
        self.assertEqual(buser.bridge_id, 100)
        self.assertEqual(buser.netid, 'not_in_pws')
        buser = busers[1]
        self.assertEqual(buser.bridge_id, 194)
        self.assertEqual(buser.netid, 'ellen')
        buser = busers[2]
        self.assertEqual(buser.bridge_id, 195)
        self.assertEqual(buser.netid, 'javerage')
        buser = busers[3]
        self.assertEqual(buser.bridge_id, 198)
        self.assertEqual(buser.netid, 'tyler')
        buser = busers[4]
        self.assertEqual(buser.bridge_id, 199)
        self.assertEqual(buser.netid, 'alumni')
        buser = busers[5]
        self.assertEqual(buser.bridge_id, 200)
        self.assertEqual(buser.netid, 'leftuw')
        buser = busers[6]
        self.assertEqual(buser.bridge_id, 204)
        self.assertEqual(buser.netid, 'retiree')
        buser = busers[7]
        self.assertEqual(buser.bridge_id, 101)
        self.assertEqual(buser.netid, 'not_accessed')

    def test_delete_bridge_user(self):
        # normal case
        user = get_mock_bridge_user(0,
                                    'leftuw',
                                    "leftuw@uw.edu",
                                    "Who LEFT",
                                    "WHO",
                                    "LEFT",
                                    "10000000000000000000000000000FFF")
        self.assertRaises(DataFailureException,
                          TestBridge.bridge.delete_bridge_user,
                          user)
        user.bridge_id = 200
        self.assertTrue(TestBridge.bridge.delete_bridge_user(user))

    def test_change_uwnetid(self):
        buser = TestBridge.bridge.get_user_by_bridgeid(198)
        self.assertEqual(buser.netid, 'tyler')

        uw_acc = UwAccount(netid='faculty',
                           bridge_id=198,
                           prev_netid='tyler',
                           last_updated=get_now())
        bridge_user = TestBridge.bridge.change_uwnetid(uw_acc)
        self.assertEqual(bridge_user.netid, 'faculty')

    def test_get_bridge_user(self):
        self.assertRaises(DataFailureException,
                          TestBridge.bridge.get_user_by_uwnetid,
                          "error500")

        self.assertIsNone(TestBridge.bridge.get_user_by_uwnetid("none"))

        # terminated
        self.assertIsNone(TestBridge.bridge.get_user_by_uwnetid("staff"))

        buser = TestBridge.bridge.get_user_by_uwnetid("javerage")
        self.assertIsNotNone(buser)
        self.assertEqual(buser.bridge_id, 195)
        self.assertEqual(buser.netid, "javerage")
        self.assertEqual(len(buser.custom_fields), 17)

        buser = TestBridge.bridge.get_user_by_bridgeid(204)
        self.assertIsNotNone(buser)
        self.assertEqual(buser.bridge_id, 204)
        self.assertEqual(buser.netid, 'retiree')
        self.assertEqual(len(buser.custom_fields), 1)

        self.assertRaises(DataFailureException,
                          TestBridge.bridge.get_user_by_bridgeid,
                          250)

    def test_restore_bridge_user(self):
        uw_acc = UwAccount(netid='staff',
                           bridge_id=196,
                           last_updated=get_now())
        buser = TestBridge.bridge.restore_bridge_user(uw_acc)
        self.assertEqual(buser.netid, 'staff')

        uw_acc = UwAccount(netid='staff',
                           last_updated=get_now())
        buser = TestBridge.bridge.restore_bridge_user(uw_acc)
        self.assertEqual(buser.bridge_id, 196)

        self.assertRaises(DataFailureException,
                          TestBridge.bridge.restore_bridge_user,
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
        ret_user = TestBridge.bridge.update_user(user)
        self.assertEqual(ret_user.netid, "faculty")

        user = get_mock_bridge_user(300,
                                    'none',
                                    "none@uw.edu",
                                    "No Name",
                                    "No",
                                    "Name",
                                    "10000000000000000000000000000000")
        self.assertRaises(DataFailureException,
                          TestBridge.bridge.update_user, user)

    def test_get_all_authors(self):
        busers = TestBridge.bridge.get_all_authors()
        self.assertEqual(len(busers), 2)
        self.assertTrue(busers[0].roles[0].is_author())
        self.assertTrue(busers[1].roles[0].is_author())
