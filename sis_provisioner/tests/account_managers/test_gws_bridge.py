from django.test import TransactionTestCase
from restclients_core.exceptions import DataFailureException
from sis_provisioner.dao.hrp import get_worker
from sis_provisioner.dao.pws import get_person
from sis_provisioner.models import UwAccount, get_now
from sis_provisioner.account_managers.bridge_worker import BridgeWorker
from sis_provisioner.account_managers.gws_bridge import GwsBridgeLoader
from sis_provisioner.tests import (
    fdao_pws_override, fdao_gws_override, fdao_bridge_override)
from sis_provisioner.tests.dao import get_mock_bridge_user
from sis_provisioner.tests.account_managers import (
    set_uw_account, set_db_records, set_db_err_records)


@fdao_bridge_override
@fdao_gws_override
@fdao_pws_override
class TestGwsBridgeLoader(TransactionTestCase):

    def test_del_bridge_account(self):
        loader = GwsBridgeLoader(BridgeWorker())
        ellen = loader.get_bridge().get_user_by_uwnetid('ellen')
        self.assertFalse(loader.del_bridge_account(ellen))

        retiree = loader.get_bridge().get_user_by_uwnetid('retiree')
        self.assertTrue(loader.del_bridge_account(retiree))
        self.assertEqual(loader.get_deleted_count(), 1)

    def test_fetch_users(self):
        loader = GwsBridgeLoader(BridgeWorker())
        user_list = loader.fetch_users()
        self.assertEqual(len(user_list), 7)
        self.assertEqual(sorted(user_list),
                         ['affiemp', 'error500', 'faculty', 'javerage',
                          'not_in_pws', 'retiree', 'staff'])

    def test_is_priority_change(self):
        loader = GwsBridgeLoader(BridgeWorker())
        uw_acc = UwAccount.objects.create(netid="affiemp")
        self.assertTrue(loader.is_priority_change(uw_acc))

        uw_acc = set_uw_account("faculty")
        uw_acc.prev_netid = "tyler"
        self.assertTrue(loader.is_priority_change(uw_acc))

        uw_acc = set_uw_account("leftuw")
        uw_acc.terminate_at = get_now()
        self.assertTrue(loader.is_priority_change(uw_acc))

        uw_acc = set_uw_account("staff")
        uw_acc.disabled = True
        self.assertTrue(loader.is_priority_change(uw_acc))

    def test_match_bridge_account(self):
        # 500 error
        uw_acc = set_uw_account("error500")
        loader = GwsBridgeLoader(BridgeWorker())
        self.assertRaises(DataFailureException,
                          loader.match_bridge_account,
                          uw_acc)

        # account not exist
        uw_acc = set_uw_account("affiemp")
        loader = GwsBridgeLoader(BridgeWorker())
        bri_acc = loader.match_bridge_account(uw_acc)
        self.assertIsNone(bri_acc)

        # account is deleted
        uw_acc = set_uw_account("staff")
        bri_acc = loader.match_bridge_account(uw_acc)
        self.assertIsNone(bri_acc)

        # exists an account with a prior netid
        uw_acc = set_uw_account("faculty")
        uw_acc.prev_netid = 'tyler'
        bri_acc = loader.match_bridge_account(uw_acc)
        self.assertEqual(bri_acc.netid, 'tyler')

        # exists two accounts (one with Lreaning History one without),
        # pick the one with LH
        uw_acc = set_uw_account("retiree")
        uw_acc.bridge_id = 204
        uw_acc.prev_netid = "ellen"
        uw_acc1 = set_uw_account("ellen")
        bri_acc = loader.match_bridge_account(uw_acc)
        self.assertEqual(bri_acc.netid, 'ellen')
        self.assertEqual(bri_acc.bridge_id, 194)

    def test_apply_change_to_bridge(self):
        loader = GwsBridgeLoader(BridgeWorker())

        # add new account
        uw_acc = set_uw_account("affiemp")
        affiemp = get_person("affiemp")
        loader.apply_change_to_bridge(uw_acc, affiemp)
        self.assertEqual(loader.get_new_user_count(), 1)
        self.assertEqual(loader.get_updated_count(), 0)

        # restore
        uw_acc = set_uw_account("staff")
        uw_acc.set_bridge_id(196)
        uw_acc.set_disable()
        staff = get_person("staff")
        loader.apply_change_to_bridge(uw_acc, staff)
        self.assertEqual(loader.get_restored_count(), 1)
        self.assertEqual(loader.get_updated_count(), 1)

        # change uid and update
        uw_acc = set_uw_account('faculty')
        uw_acc.prev_netid = 'tyler'
        uw_acc.set_bridge_id(198)
        faculty = get_person("faculty")
        loader.apply_change_to_bridge(uw_acc, faculty)
        self.assertEqual(loader.get_netid_changed_count(), 1)
        self.assertEqual(loader.get_updated_count(), 2)

        # change uid and update
        uw_acc = set_uw_account("retiree")
        uw_acc.bridge_id = 204
        uw_acc.prev_netid = "ellen"
        retiree = get_person("retiree")
        loader.apply_change_to_bridge(uw_acc, retiree)
        self.assertEqual(loader.get_netid_changed_count(), 2)
        self.assertEqual(loader.get_updated_count(), 3)

    def test_load_gws(self):
        with self.settings(ERRORS_TO_ABORT_LOADER=[]):
            set_db_records()
            loader = GwsBridgeLoader(BridgeWorker())
            loader.load()
            self.assertEqual(loader.get_total_count(), 7)
            self.assertEqual(loader.get_new_user_count(), 1)
            self.assertEqual(loader.get_restored_count(), 1)
            self.assertEqual(loader.get_netid_changed_count(), 2)
            self.assertEqual(loader.get_updated_count(), 3)
            self.assertTrue(loader.has_error())

    def test_load_abort(self):
        with self.settings(ERRORS_TO_ABORT_LOADER=[500]):
            set_db_err_records()
            loader = GwsBridgeLoader(BridgeWorker())
            self.assertRaises(DataFailureException, loader.load)

    def test_account_not_changed(self):
        loader = GwsBridgeLoader(BridgeWorker())
        uw_account = set_uw_account('javerage')
        uw_account.set_bridge_id(195)
        person = get_person('javerage')
        hrp_wkr = get_worker(person)
        bridge_account = loader.worker.get_bridge_user_to_add(person,
                                                              hrp_wkr)
        self.assertTrue(
            loader.account_not_changed(bridge_account, person, hrp_wkr))

        bridge_account = loader.get_bridge().get_user_by_uwnetid(
            person.uwnetid)
        self.assertTrue(
            loader.account_not_changed(bridge_account, person, hrp_wkr))
