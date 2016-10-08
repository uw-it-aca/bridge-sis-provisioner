from django.conf import settings
from django.test import TransactionTestCase
from sis_provisioner.test import FBRI
from sis_provisioner.dao.user import get_user_by_netid
from sis_provisioner.models import UwBridgeUser, get_now, ACTION_UPDATE,\
    ACTION_NEW, ACTION_CHANGE_REGID, ACTION_RESTORE
from sis_provisioner.account_managers.reload_bridge import Reloader
from sis_provisioner.account_managers.bridge_worker import BridgeWorker


class TestReloader(TransactionTestCase):

    def test_add_new(self):
        with self.settings(RESTCLIENTS_PWS_BRIDGE_DAO_CLASS=FBRI):
            user = UwBridgeUser(netid='javerage',
                                regid="9136CCB8F66711D5BE060004AC494FFE",
                                last_visited_at=get_now(),
                                action_priority=ACTION_NEW,
                                email='javerage@uw.edu',
                                first_name="James",
                                last_name="New")
            user.save()
            loader = Reloader(BridgeWorker())
            loader.load()
            bri_users = loader.get_users_to_process()
            self.assertEqual(len(bri_users), 1)
            self.assertEqual(loader.get_total_count(), 1)
            self.assertEqual(loader.get_new_user_count(), 1)
            self.assertEqual(loader.get_loaded_count(), 1)
            self.assertEqual(loader.get_netid_changed_count(), 0)
            self.assertEqual(loader.get_regid_changed_count(), 0)

    def test_update(self):
        with self.settings(RESTCLIENTS_PWS_BRIDGE_DAO_CLASS=FBRI):
            user = UwBridgeUser(netid='javerage',
                                regid="9136CCB8F66711D5BE060004AC494FFE",
                                last_visited_at=get_now(),
                                action_priority=ACTION_UPDATE,
                                email='javerage@uw.edu',
                                first_name="James",
                                last_name="Changed")
            user.save()
            loader = Reloader(BridgeWorker())
            loader.load()
            bri_users = loader.get_users_to_process()
            self.assertEqual(len(bri_users), 1)
            self.assertEqual(loader.get_total_count(), 1)
            self.assertEqual(loader.get_new_user_count(), 0)
            self.assertEqual(loader.get_loaded_count(), 1)
            self.assertEqual(loader.get_netid_changed_count(), 0)
            self.assertEqual(loader.get_regid_changed_count(), 0)

    def test_changed_netid(self):
        with self.settings(RESTCLIENTS_PWS_BRIDGE_DAO_CLASS=FBRI):
            user = UwBridgeUser(netid='javerage',
                                bridge_id=195,
                                regid="0136CCB8F66711D5BE060004AC494FFE",
                                prev_netid='old',
                                action_priority=ACTION_UPDATE,
                                last_visited_at=get_now(),
                                email='javerage@uw.edu',
                                first_name="Changed",
                                last_name="Netid")
            user.save()
            loader = Reloader(BridgeWorker())
            loader.load()
            bri_users = loader.get_users_to_process()
            self.assertEqual(len(bri_users), 1)
            self.assertEqual(loader.get_total_count(), 1)
            self.assertEqual(loader.get_loaded_count(), 1)
            self.assertEqual(loader.get_netid_changed_count(), 1)
            self.assertEqual(loader.get_regid_changed_count(), 0)

    def test_changed_regid(self):
        with self.settings(RESTCLIENTS_PWS_BRIDGE_DAO_CLASS=FBRI):
            user = UwBridgeUser(netid='javerage',
                                regid="0136CCB8F66711D5BE060004AC494FFE",
                                action_priority=ACTION_CHANGE_REGID,
                                last_visited_at=get_now(),
                                email='javerage@uw.edu',
                                first_name="Changed",
                                last_name="Regid")
            user.save()
            loader = Reloader(BridgeWorker())
            loader.load()
            bri_users = loader.get_users_to_process()
            self.assertEqual(len(bri_users), 1)
            self.assertEqual(loader.get_total_count(), 1)
            self.assertEqual(loader.get_loaded_count(), 1)
            self.assertEqual(loader.get_netid_changed_count(), 0)
            self.assertEqual(loader.get_regid_changed_count(), 1)

    def test_delete(self):
        with self.settings(RESTCLIENTS_PWS_BRIDGE_DAO_CLASS=FBRI):
            user = UwBridgeUser(netid='javerage',
                                regid="0136CCB8F66711D5BE060004AC494FFE",
                                bridge_id=195,
                                last_visited_at=get_now(),
                                terminate_at=get_now(),
                                last_name="Delete")
            user.save()
            loader = Reloader(BridgeWorker())
            loader.load()
            self.assertEqual(loader.get_total_count(), 1)
            self.assertEqual(loader.get_deleted_count(), 1)

    def test_restore(self):
        with self.settings(RESTCLIENTS_PWS_BRIDGE_DAO_CLASS=FBRI):
            user = UwBridgeUser(netid='javerage',
                                bridge_id=195,
                                regid="0136CCB8F66711D5BE060004AC494FFE",
                                last_visited_at=get_now(),
                                last_name="Restore")
            user.action_priority = ACTION_RESTORE
            user.save()
            loader = Reloader(BridgeWorker())
            loader.load()
            self.assertEqual(loader.get_total_count(), 1)
            self.assertEqual(loader.get_restored_count(), 1)
