import logging
from django.test import TransactionTestCase
from uw_bridge.models import BridgeUser, BridgeCustomField
from sis_provisioner.dao import DataFailureException
from sis_provisioner.dao.hrp import get_worker
from sis_provisioner.dao.uw_account import get_by_netid
from sis_provisioner.dao.pws import get_person
from sis_provisioner.account_managers.bridge_worker import BridgeWorker
from sis_provisioner.tests import (
    fdao_pws_override, fdao_bridge_override)
from sis_provisioner.tests.dao import get_mock_bridge_user
from sis_provisioner.tests.account_managers import set_uw_account

FAC_JSON = {'uid': 'faculty@uw.edu',
            'full_name': 'William E Faculty',
            'email': 'faculty@uw.edu',
            'custom_fields': [
                {'custom_field_id': '5',
                 'value': '10000000000000000000000000000005'},
                {'custom_field_id': '6',
                 'value': '000000005'},
                {'custom_field_id': '7',
                 'value': '0000005'},
                {'custom_field_id': '11',
                 'value': '3040111000'},
                {'custom_field_id': '12',
                 'value': '21184'},
                {'custom_field_id': '13',
                 'value': 'Academic Personnel'},
                {'custom_field_id': '14',
                 'value': 'SOM:'},
                {'custom_field_id': '15',
                 'value': 'Family Medicine: Volunteer JM Academic'}],
            'first_name': 'William E',
            'last_name': 'Faculty',
            'sortable_name': 'Faculty, William E',
            'job_title': 'Clinical Associate Professor'}


@fdao_pws_override
@fdao_bridge_override
class TestBridgeWorker(TransactionTestCase):

    def test_get_bridge_user_to_add(self):
        worker = BridgeWorker()
        person = get_person('faculty')
        user = worker.get_bridge_user_to_add(person, get_worker(person))
        self.assertEqual(user.to_json(), FAC_JSON)

    def test_get_bridge_user_to_upd(self):
        person = get_person('faculty')
        worker = BridgeWorker()
        user = worker.get_bridge_user_to_upd(person,
                                             get_worker(person),
                                             BridgeUser(netid='faculty'))
        self.assertEqual(user.to_json(), FAC_JSON)

    def test_add_new_user(self):
        worker = BridgeWorker()
        uw_acc = set_uw_account('affiemp')
        person = get_person('affiemp')
        worker.add_new_user(uw_acc, person, get_worker(person))
        self.assertEqual(worker.get_new_user_count(), 1)

        person = get_person('javerage')
        worker.add_new_user(set_uw_account('javerage'), person,
                            get_worker(person))
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

    def test_not_changed(self):
        worker = BridgeWorker()
        person = get_person('faculty')
        hrp_wkr = get_worker(person)
        bridge_account = worker.get_bridge_user_to_add(person, None)
        self.assertTrue(worker.regid_not_changed(bridge_account, person))
        self.assertTrue(worker.eid_not_changed(bridge_account, person))
        self.assertTrue(worker.sid_not_changed(bridge_account, person))
        self.assertFalse(worker.pos1_budget_code_not_changed(
            bridge_account, hrp_wkr))
        self.assertFalse(worker.pos1_job_code_not_changed(
            bridge_account, hrp_wkr))
        self.assertFalse(worker.pos1_job_class_not_changed(
            bridge_account, hrp_wkr))
        self.assertFalse(worker.pos1_org_code_not_changed(
            bridge_account, hrp_wkr))
        self.assertFalse(worker.pos1_org_name_not_changed(
            bridge_account, hrp_wkr))

        bridge_account = worker.get_bridge_user_to_add(person, hrp_wkr)
        self.assertTrue(worker.pos1_budget_code_not_changed(
            bridge_account, hrp_wkr))
        self.assertTrue(worker.pos1_job_code_not_changed(
            bridge_account, hrp_wkr))
        self.assertTrue(worker.pos1_job_class_not_changed(
            bridge_account, hrp_wkr))
        self.assertTrue(worker.pos1_org_code_not_changed(
            bridge_account, hrp_wkr))
        self.assertTrue(worker.pos1_org_name_not_changed(
            bridge_account, hrp_wkr))

        person = get_person('affiemp')
        hrp_wkr = get_worker(person)
        bridge_account = worker.get_bridge_user_to_add(person, hrp_wkr)
        self.assertTrue(worker.pos1_budget_code_not_changed(
            bridge_account, hrp_wkr))
        self.assertTrue(worker.pos1_job_code_not_changed(
            bridge_account, hrp_wkr))
        self.assertTrue(worker.pos1_job_class_not_changed(
            bridge_account, hrp_wkr))
        self.assertTrue(worker.pos1_org_code_not_changed(
            bridge_account, hrp_wkr))
        self.assertTrue(worker.pos1_org_name_not_changed(
            bridge_account, hrp_wkr))
