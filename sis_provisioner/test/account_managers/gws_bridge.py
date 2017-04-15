import logging
from datetime import timedelta
from django.test import TransactionTestCase
from sis_provisioner.models import UwBridgeUser, get_now, ACTION_RESTORE,\
    ACTION_CHANGE_REGID, ACTION_UPDATE
from sis_provisioner.dao.user import get_user_by_regid
from sis_provisioner.account_managers.bridge_worker import BridgeWorker
from sis_provisioner.account_managers.gws_bridge import GwsBridgeLoader
from sis_provisioner.test import fdao_pws_override, fdao_gws_override,\
    fdao_bridge_override, fdao_hrp_override


logger = logging.getLogger(__name__)


@fdao_bridge_override
@fdao_gws_override
@fdao_pws_override
@fdao_hrp_override
class TestGwsBridgeLoader(TransactionTestCase):

    def test_load_new_users(self):
        loader = GwsBridgeLoader(BridgeWorker())
        loader.load()
        self.assertEqual(loader.get_total_count(), 12)
        self.assertEqual(loader.get_new_user_count(), 1)
        self.assertEqual(loader.get_loaded_count(), 2)
        self.assertEqual(loader.get_netid_changed_count(), 0)
        self.assertEqual(loader.get_regid_changed_count(), 0)
        self.assertTrue(loader.has_error())

    def test_load_new_users_with_hrp(self):
        loader = GwsBridgeLoader(BridgeWorker(),
                                 include_hrp=True)
        loader.load()
        self.assertEqual(loader.get_total_count(), 12)
        self.assertEqual(loader.get_new_user_count(), 1)
        self.assertEqual(loader.get_loaded_count(), 2)
        self.assertEqual(loader.get_netid_changed_count(), 0)
        self.assertEqual(loader.get_regid_changed_count(), 0)

    def test_error_case(self):
        loader = GwsBridgeLoader(BridgeWorker())
        loader.apply_change_to_bridge(None)
        self.assertEqual(loader.get_total_count(), 0)
        self.assertEqual(loader.get_new_user_count(), 0)
        self.assertEqual(loader.get_loaded_count(), 0)
        self.assertEqual(loader.get_netid_changed_count(), 0)
        self.assertEqual(loader.get_regid_changed_count(), 0)

    def test_netid_change_user(self):
        loader = GwsBridgeLoader(BridgeWorker())
        user = UwBridgeUser(netid='changed',
                            bridge_id=195,
                            prev_netid='javerage',
                            regid="9136CCB8F66711D5BE060004AC494FFE",
                            last_visited_at=get_now(),
                            display_name="James Student",
                            email="changed@uw.edu")
        user.save()
        loader.load()
        self.assertEqual(loader.get_netid_changed_count(), 1)
        self.assertEqual(loader.get_loaded_count(), 2)

    def test_regid_change_user(self):
        user = UwBridgeUser(netid='javerage',
                            regid="0136CCB8F66711D5BE060004AC494FFE",
                            email="changed@uw.edu",
                            last_visited_at=get_now(),
                            display_name="James Changed",
                            last_name="Changed")
        user.save()
        loader = GwsBridgeLoader(BridgeWorker())
        loader.load()
        self.assertRaises(UwBridgeUser.DoesNotExist,
                          get_user_by_regid,
                          "0136CCB8F66711D5BE060004AC494FFE")
        self.assertEqual(loader.get_regid_changed_count(), 1)

    def test_restore_user(self):
        user = UwBridgeUser(netid='javerage',
                            regid="9136CCB8F66711D5BE060004AC494FFE",
                            last_visited_at=get_now(),
                            terminate_at=get_now(),
                            disabled=True,
                            email='javerage@uw.edu',
                            first_name="James",
                            last_name="Changed")
        user.save()
        loader = GwsBridgeLoader(BridgeWorker())
        loader.load()
        self.assertEqual(loader.get_restored_count(), 1)
        self.assertEqual(loader.get_loaded_count(), 2)

    def test_merge_user_accounts(self):
        del_user = UwBridgeUser(netid='changed',
                                bridge_id=195,
                                regid="9136CCB8F66711D5BE060004AC494FFE",
                                action_priority=ACTION_UPDATE,
                                last_visited_at=get_now(),
                                first_name="Changed",
                                last_name="Netid")
        user = UwBridgeUser(netid='javerage',
                            bridge_id=195,
                            prev_netid='changed',
                            regid="9136CCB8F66711D5BE060004AC494FFE",
                            action_priority=ACTION_UPDATE,
                            last_visited_at=get_now(),
                            first_name="Changed",
                            last_name="Netid")
        loader = GwsBridgeLoader(BridgeWorker())
        loader.merge_user_accounts(del_user, user)
        self.assertEqual(loader.get_deleted_count(), 0)
        self.assertTrue(loader.has_error())
