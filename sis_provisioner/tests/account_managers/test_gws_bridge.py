from django.test import TransactionTestCase
from restclients_core.exceptions import DataFailureException
from sis_provisioner.dao.bridge import get_user_by_uwnetid
from sis_provisioner.dao.pws import get_person
from sis_provisioner.models import UwAccount
from sis_provisioner.account_managers.bridge_worker import BridgeWorker
from sis_provisioner.account_managers.gws_bridge import GwsBridgeLoader
from sis_provisioner.tests import (
    fdao_pws_override, fdao_gws_override, fdao_bridge_override)
from sis_provisioner.tests.account_managers import (
    set_uw_account, set_db_records)


@fdao_bridge_override
@fdao_gws_override
@fdao_pws_override
class TestGwsBridgeLoader(TransactionTestCase):

    def test_del_bridge_account(self):
        exi, ellen = get_user_by_uwnetid('ellen')
        loader = GwsBridgeLoader(BridgeWorker())
        self.assertFalse(loader.del_bridge_account(ellen))

        exi, retiree = get_user_by_uwnetid('retiree')
        self.assertTrue(loader.del_bridge_account(retiree))
        self.assertEqual(loader.get_deleted_count(), 1)

    def test_fetch_users(self):
        loader = GwsBridgeLoader(BridgeWorker())
        user_list = loader.fetch_users()
        self.assertEqual(len(user_list), 7)
        self.assertEqual(sorted(user_list),
                         ['affiemp', 'error500', 'faculty', 'javerage',
                          'not_in_pws', 'retiree', 'staff'])

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
        exi, bri_acc = loader.match_bridge_account(uw_acc)
        self.assertFalse(exi)
        self.assertIsNone(bri_acc)

        # account is deleted
        uw_acc = set_uw_account("staff")
        exi, bri_acc = loader.match_bridge_account(uw_acc)
        self.assertTrue(exi)
        self.assertIsNone(bri_acc)

        # exists an account with a prior netid
        uw_acc = set_uw_account("faculty")
        uw_acc.prev_netid = 'tyler'
        exi, bri_acc = loader.match_bridge_account(uw_acc)
        self.assertTrue(exi)
        self.assertEqual(bri_acc.netid, 'tyler')

        # exists two accounts (one with Lreaning History one without),
        # pick the one with LH
        uw_acc = set_uw_account("retiree")
        uw_acc.bridge_id = 204
        uw_acc.prev_netid = "ellen"
        uw_acc1 = set_uw_account("ellen")
        exi, bri_acc = loader.match_bridge_account(uw_acc)
        self.assertTrue(exi)
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
        staff = get_person("staff")
        loader.apply_change_to_bridge(uw_acc, affiemp)
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
            set_db_records()
            loader = GwsBridgeLoader(BridgeWorker())
            self.assertRaises(DataFailureException, loader.load)
