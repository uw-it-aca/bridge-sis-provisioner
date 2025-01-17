# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TransactionTestCase
from unittest.mock import patch
from restclients_core.exceptions import DataFailureException
from sis_provisioner.dao.hrp import get_worker
from sis_provisioner.dao.pws import get_person
from sis_provisioner.account_managers.bridge_worker import BridgeWorker
from sis_provisioner.account_managers.gws_bridge import GwsBridgeLoader
from sis_provisioner.tests import (
    fdao_pws_override, fdao_gws_override, fdao_bridge_override)
from sis_provisioner.tests.dao import get_mock_bridge_user
from sis_provisioner.tests.account_managers import (
    set_uw_account, set_db_records, set_db_err_records)


users = ['affiemp', 'error500', 'faculty', 'javerage',
         'not_in_pws', 'retiree', 'staff']


@fdao_bridge_override
@fdao_gws_override
@fdao_pws_override
class TestGwsBridgeLoader(TransactionTestCase):

    def test_del_bridge_account(self):
        loader = GwsBridgeLoader(BridgeWorker())
        self.assertTrue(loader.update_existing_accs())
        ellen = loader.get_bridge().get_user_by_uwnetid('ellen')
        self.assertFalse(loader.del_bridge_account(ellen))

        retiree = loader.get_bridge().get_user_by_uwnetid('retiree')
        self.assertTrue(loader.del_bridge_account(retiree))
        self.assertEqual(loader.get_deleted_count(), 1)

    @patch('sis_provisioner.dao.gws._get_start_timestamp',
           return_value=1626215400, spec=True)
    def test_fetch_users(self, mock_fn):
        with self.settings(BRIDGE_GMEMBER_ADD_WINDOW=12):
            loader = GwsBridgeLoader(BridgeWorker())
            user_list = loader.fetch_users()
            self.assertEqual(len(user_list), 1)
            self.assertEqual(user_list, ['added'])

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

    @patch.object(GwsBridgeLoader, 'fetch_users',
                  return_value=users, spec=True)
    def test_load_gws(self, mock_fn):
        with self.settings(ERRORS_TO_ABORT_LOADER=[],
                           BRIDGE_USER_WORK_POSITIONS=2):
            set_db_records()
            loader = GwsBridgeLoader(BridgeWorker())
            loader.load()
            self.assertEqual(loader.get_total_count(), 7)
            self.assertEqual(loader.get_total_checked_users(), 6)
            self.assertEqual(loader.get_new_user_count(), 1)
            self.assertEqual(loader.get_restored_count(), 1)
            self.assertEqual(loader.get_netid_changed_count(), 2)
            self.assertEqual(loader.get_updated_count(), 3)
            self.assertTrue(loader.has_error())

    @patch.object(GwsBridgeLoader, 'fetch_users',
                  return_value=[], spec=True)
    def test_load_abort(self, mock_fn):
        with self.settings(ERRORS_TO_ABORT_LOADER=[500],
                           BRIDGE_USER_WORK_POSITIONS=2):
            loader = GwsBridgeLoader(BridgeWorker())
            loader.load()
            self.assertEqual(loader.get_total_count(), 0)

    def test_account_not_changed(self):
        with self.settings(BRIDGE_USER_WORK_POSITIONS=2):
            set_db_records()
            loader = GwsBridgeLoader(BridgeWorker())
            person = get_person('javerage')
            hrp_wkr = get_worker(person)
            bridge_account = loader.get_bridge().get_user_by_uwnetid(
                'javerage')
            self.assertTrue(
                loader.account_not_changed(bridge_account, person, hrp_wkr))

    def test_field_not_changed(self):
        with self.settings(BRIDGE_USER_WORK_POSITIONS=2):
            loader = GwsBridgeLoader(BridgeWorker())

            person = get_person('javerage')
            hrp_wkr = get_worker(person)
            bridge_account = loader.get_bridge().get_user_by_uwnetid(
                'javerage')
            self.assertTrue(loader.regid_not_changed(bridge_account, person))
            self.assertTrue(loader.eid_not_changed(bridge_account, person))
            self.assertTrue(loader.sid_not_changed(bridge_account, person))
            self.assertTrue(loader.pos_data_not_changed(
                bridge_account, hrp_wkr))
            self.assertTrue(loader.hired_date_not_changed(
                bridge_account, hrp_wkr))

            person = get_person('faculty')
            hrp_wkr = get_worker(person)
            bridge_account = loader.get_bridge().get_user_by_uwnetid('tyler')
            self.assertFalse(loader.regid_not_changed(bridge_account, person))
            self.assertFalse(loader.eid_not_changed(bridge_account, person))
            self.assertFalse(loader.sid_not_changed(bridge_account, person))
            self.assertFalse(loader.pos_data_not_changed(
                bridge_account, hrp_wkr))
            self.assertFalse(loader.hired_date_not_changed(
                bridge_account, hrp_wkr))
