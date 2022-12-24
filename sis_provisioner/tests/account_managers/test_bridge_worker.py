# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging
from django.test import TransactionTestCase
from uw_bridge.models import BridgeUser, BridgeCustomField
from sis_provisioner.dao import DataFailureException
from sis_provisioner.dao.hrp import get_worker
from sis_provisioner.dao.uw_account import get_by_netid
from sis_provisioner.dao.pws import get_person
from sis_provisioner.account_managers.bridge_worker import BridgeWorker
from sis_provisioner.tests import (
    fdao_pws_override, fdao_bridge_override, fdao_hrp_override)
from sis_provisioner.tests.dao import get_mock_bridge_user
from sis_provisioner.tests.account_managers import (
    set_uw_account, set_db_records)


@fdao_pws_override
@fdao_bridge_override
@fdao_hrp_override
class TestBridgeWorker(TransactionTestCase):

    def test_get_bridge_user_to_add(self):
        set_db_records()
        # self.maxDiff = None
        worker = BridgeWorker()
        person = get_person('faculty')
        user = worker.get_bridge_user_to_add(person, get_worker(person))
        self.assertEqual(
            user.to_json_post(),
            {'users': [
                {'uid': 'faculty@uw.edu',
                 'full_name': 'William E Faculty',
                 'email': 'faculty@uw.edu',
                 'custom_field_values': [
                     {'custom_field_id': '5',
                      'value': '10000000000000000000000000000005'},
                     {'custom_field_id': '6',
                      'value': '000000005'},
                     {'custom_field_id': '7',
                      'value': '0000005'},
                     {'custom_field_id': '11',
                      'value': '681925 WORKDAY DEFAULT DEPTBG'},
                     {'custom_field_id': '13',
                      'value': 'Academic Personnel'},
                     {'custom_field_id': '12',
                      'value': '21184'},
                     {'custom_field_id': '17',
                      'value': 'Seattle Campus'},
                     {'custom_field_id': '14',
                      'value': 'SOM'},
                     {'custom_field_id': '15',
                      'value': 'Family Medicine: King Pierce JM Academic'},
                     {'custom_field_id': '16',
                      'value': ''},
                     {'custom_field_id': '21',
                      'value': None},
                     {'custom_field_id': '23',
                      'value': None},
                     {'custom_field_id': '22',
                      'value': None},
                     {'custom_field_id': '27',
                      'value': None},
                     {'custom_field_id': '24',
                      'value': None},
                     {'custom_field_id': '25',
                      'value': None},
                     {'custom_field_id': '26',
                      'value': None}],
                 'first_name': 'William E',
                 'last_name': 'Faculty',
                 'sortable_name': 'Faculty, William E',
                 'manager_id': 196,
                 'job_title': 'Clinical Associate Professor'}]})

    def test_set_bridge_user_to_update(self):
        set_db_records()
        person = get_person('faculty')
        worker = BridgeWorker()
        user = worker.bridge.get_user_by_uwnetid('tyler')
        worker.set_bridge_user_to_update(person, get_worker(person), user)
        # self.maxDiff = None
        self.assertEqual(
            user.to_json_patch(),
            {'user': {
                'id': 198,
                'uid': 'faculty@uw.edu',
                'full_name': 'William E Faculty',
                'email': 'faculty@uw.edu',
                'first_name': 'William E',
                'last_name': 'Faculty',
                'sortable_name': 'Faculty, William E',
                'job_title': 'Clinical Associate Professor',
                'manager_id': 196,
                'custom_field_values': [
                    {'custom_field_id': '5',
                     'value': '10000000000000000000000000000005',
                     'id': '1'},
                    {'custom_field_id': '7',
                     'id': '3',
                     'value': '0000005'},
                    {'custom_field_id': '11',
                     'value': '681925 WORKDAY DEFAULT DEPTBG',
                     'id': '4'},
                    {'custom_field_id': '13',
                     'value': 'Academic Personnel',
                     'id': '5'},
                    {'custom_field_id': '12',
                     'value': '21184',
                     'id': '6'},
                    {'custom_field_id': '17',
                     'value': 'Seattle Campus',
                     'id': '7'},
                    {'custom_field_id': '14',
                     'value': 'SOM',
                     'id': '8'},
                    {'custom_field_id': '15',
                     'value': 'Family Medicine: King Pierce JM Academic',
                     'id': '9'},
                    {'custom_field_id': '16', 'value': '', 'id': '10'},
                    {'custom_field_id': '21', 'value': None, 'id': '24'},
                    {'custom_field_id': '23', 'value': None, 'id': '25'},
                    {'custom_field_id': '22', 'value': None, 'id': '26'},
                    {'custom_field_id': '27', 'value': None, 'id': '27'},
                    {'custom_field_id': '24', 'value': None, 'id': '28'},
                    {'custom_field_id': '25', 'value': None, 'id': '29'},
                    {'custom_field_id': '26', 'value': None, 'id': '30'},
                    {'custom_field_id': '6', 'value': '000000005'}]}})

        worker = BridgeWorker()
        user = worker.bridge.get_user_by_uwnetid('ellen')
        person = get_person('retiree')
        worker.set_bridge_user_to_update(person, get_worker(person), user)
        # self.maxDiff = None
        self.assertEqual(
            user.to_json_patch(),
            {'user': {
                'uid': 'retiree@uw.edu',
                'full_name': 'Ellen Louise Retiree',
                'email': 'retiree@uw.edu',
                'id': 194,
                'first_name': 'Ellen',
                'last_name': 'Retiree',
                'sortable_name': 'Retiree, Ellen',
                'manager_id': None,
                'custom_field_values': [
                    {'custom_field_id': '5',
                     'value': '10000000000000000000000000000006',
                     'id': '1'},
                    {'custom_field_id': '6',
                     'value': '000000006',
                     'id': '2'},
                    {'custom_field_id': '7', 'value': '0000006', 'id': '3'},
                    {'custom_field_id': '11', 'value': None, 'id': '4'},
                    {'custom_field_id': '13', 'value': None, 'id': '5'},
                    {'custom_field_id': '12', 'value': None, 'id': '6'},
                    {'custom_field_id': '17', 'value': None, 'id': '7'},
                    {'custom_field_id': '14', 'value': None, 'id': '8'},
                    {'custom_field_id': '15', 'value': None, 'id': '9'},
                    {'custom_field_id': '16', 'value': None, 'id': '10'},
                    {'custom_field_id': '21', 'value': None, 'id': '24'},
                    {'custom_field_id': '23', 'value': None, 'id': '25'},
                    {'custom_field_id': '22', 'value': None, 'id': '26'},
                    {'custom_field_id': '27', 'value': None, 'id': '27'},
                    {'custom_field_id': '24', 'value': None, 'id': '28'},
                    {'custom_field_id': '25', 'value': None, 'id': '29'},
                    {'custom_field_id': '26', 'value': None, 'id': '30'}]}})

    def test_add_new_user(self):
        worker = BridgeWorker()
        person = get_person('affiemp')
        uw_acc = set_uw_account('affiemp')
        worker.add_new_user(uw_acc, person, get_worker(person))
        self.assertEqual(worker.get_new_user_count(), 1)

        person = get_person('javerage')
        uw_acc = set_uw_account('javerage')
        worker.add_new_user(uw_acc, person, get_worker(person))
        self.assertTrue(worker.has_err())

    def test_delete_user(self):
        worker = BridgeWorker()
        bri_acc = worker.bridge.get_user_by_uwnetid('retiree')
        self.assertTrue(worker.delete_user(bri_acc))
        self.assertEqual(worker.get_deleted_count(), 1)

        bri_acc.bridge_id = 0
        self.assertFalse(worker.delete_user(bri_acc))
        self.assertTrue(worker.has_err())

    def test_restore_user(self):
        uw_acc = set_uw_account('staff')
        uw_acc.set_bridge_id(196)
        worker = BridgeWorker()
        bri_acc = worker.restore_user(uw_acc)
        self.assertIsNotNone(bri_acc)
        self.assertFalse(uw_acc.disabled)
        self.assertEqual(worker.get_restored_count(), 1)

        self.assertIsNone(worker.restore_user(set_uw_account('javerage')))
        self.assertTrue(worker.has_err())

    def test_update_uid(self):
        worker = BridgeWorker()
        uw_acc = set_uw_account('faculty')
        uw_acc.prev_netid = 'tyler'
        uw_acc.set_bridge_id(198)
        self.assertTrue(uw_acc.netid_changed())
        worker.update_uid(uw_acc)
        self.assertEqual(worker.get_netid_changed_count(), 1)
        self.assertFalse(worker.has_err())

        self.assertRaises(DataFailureException,
                          worker.update_uid, set_uw_account('javerage'))

    def test_update_user_with_uid_change(self):
        worker = BridgeWorker()
        uw_acc = set_uw_account('faculty')
        uw_acc.prev_netid = 'tyler'
        uw_acc.set_bridge_id(198)
        self.assertTrue(uw_acc.netid_changed())
        person = get_person('faculty')
        bri_acc = worker.bridge.get_user_by_uwnetid('tyler')
        worker.update_user(bri_acc, uw_acc, person, get_worker(person))
        self.assertEqual(worker.get_netid_changed_count(), 1)
        self.assertEqual(worker.get_updated_count(), 1)

        uw_acc = set_uw_account('retiree')
        uw_acc.prev_netid = 'ellen'
        uw_acc.set_bridge_id(194)
        self.assertTrue(uw_acc.netid_changed())
        person = get_person('retiree')
        bri_acc = worker.bridge.get_user_by_uwnetid('ellen')
        worker.update_user(bri_acc, uw_acc, person, get_worker(person))
        self.assertEqual(worker.get_netid_changed_count(), 2)
        self.assertEqual(worker.get_updated_count(), 2)

    def test_update_user_wo_uid_change(self):
        worker = BridgeWorker()
        uw_acc = set_uw_account('staff')
        uw_acc.set_bridge_id(196)
        person = get_person('staff')
        bri_acc = worker.restore_user(uw_acc)
        worker.update_user(bri_acc, uw_acc, person, get_worker(person))
        self.assertEqual(worker.get_netid_changed_count(), 0)
        self.assertEqual(worker.get_updated_count(), 1)

        worker = BridgeWorker()
        bridge_account = worker.bridge.get_user_by_uwnetid('retiree')
        person = get_person('retiree')
        worker.update_user(bridge_account,
                           set_uw_account('retiree'),
                           person,
                           get_worker(person))
        self.assertEqual(worker.get_updated_count(), 0)
        self.assertTrue(worker.has_err())

    def test_update_custom_field(self):
        worker = BridgeWorker()
        bridge_account = worker.bridge.get_user_by_uwnetid('tyler')
        cf = bridge_account.get_custom_field(
            BridgeCustomField.POS1_BUDGET_CODE)
        value = "12345"
        worker.update_custom_field(bridge_account,
                                   BridgeCustomField.POS1_BUDGET_CODE,
                                   value)
        self.assertEqual(cf.value, value)

    def test_update_user_role(self):
        worker = BridgeWorker()
        bridge_account = worker.bridge.get_user_by_uwnetid('tyler')
        worker.update_user_role(bridge_account)
        self.assertTrue(worker.has_err())
