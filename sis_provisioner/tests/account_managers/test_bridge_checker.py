# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TransactionTestCase
from datetime import timedelta
from sis_provisioner.models import get_now
from sis_provisioner.dao.pws import get_person
from sis_provisioner.dao.uw_account import get_by_netid
from sis_provisioner.account_managers.bridge_checker import BridgeChecker
from sis_provisioner.account_managers.bridge_worker import BridgeWorker
from sis_provisioner.tests import (
    fdao_gws_override, fdao_pws_override, fdao_bridge_override)
from sis_provisioner.tests.dao import get_mock_bridge_user
from sis_provisioner.tests.account_managers import (
    set_uw_account, set_db_records)


@fdao_bridge_override
@fdao_gws_override
@fdao_pws_override
class TestBridgeUserChecker(TransactionTestCase):

    def test_fetch_users(self):
        loader = BridgeChecker(BridgeWorker())
        bridge_users = loader.fetch_users()
        self.assertEqual(len(bridge_users), 8)

    def test_take_action(self):
        set_db_records()
        loader = BridgeChecker(BridgeWorker())
        bri_acc = loader.get_bridge().get_user_by_uwnetid('alumni')
        alumni = get_person('alumni')
        self.assertFalse(loader.in_uw_groups('alumni'))
        loader.take_action(alumni, bri_acc)
        self.assertEqual(loader.get_netid_changed_count(), 0)
        self.assertEqual(loader.get_deleted_count(), 0)
        self.assertEqual(loader.get_restored_count(), 0)
        self.assertEqual(loader.get_updated_count(), 1)
        self.assertFalse(loader.has_error())

        bri_acc = loader.get_bridge().get_user_by_uwnetid('javerage')
        javerage = get_person('javerage')
        loader.take_action(javerage, bri_acc)
        self.assertEqual(loader.get_netid_changed_count(), 0)
        self.assertEqual(loader.get_deleted_count(), 0)
        self.assertEqual(loader.get_restored_count(), 0)
        self.assertEqual(loader.get_updated_count(), 1)
        self.assertFalse(loader.has_error())
        self.assertEqual(len(loader.get_error_report()), 0)

        bri_acc = loader.get_bridge().get_user_by_uwnetid('tyler')
        tyler = get_person('tyler')
        loader.take_action(tyler, bri_acc)
        self.assertEqual(loader.get_netid_changed_count(), 1)
        self.assertEqual(loader.get_updated_count(), 2)
        self.assertFalse(loader.has_error())

        # mis-matched accounts
        loader = BridgeChecker(BridgeWorker())
        uw_acc = get_by_netid('javerage')
        bri_acc = get_mock_bridge_user(
            195,
            "javge",
            "javerage@uw.edu",
            "Average Joseph Student",
            "Average Joseph",
            "Student",
            "9136CCB8F66711D5BE060004AC494FFE")
        loader.take_action(javerage, bri_acc)
        self.assertTrue(loader.has_error())

        loader = BridgeChecker(BridgeWorker())
        uw_acc.prev_netid = 'javerage0'
        uw_acc.save()
        loader.take_action(javerage, bri_acc)
        self.assertTrue(loader.has_error())

        # 500 Error
        loader = BridgeChecker(BridgeWorker())
        error500 = get_person(get_person('error500'))
        bri_acc = get_mock_bridge_user(
            250,
            "error500",
            "error500@uw.edu",
            "Average Error",
            "Average",
            "Error",
            "9136CCB8F66711D5BE060004AC494FFE")
        loader.take_action(error500, bri_acc)
        self.assertTrue(loader.has_error())

    def test_has_accessed(self):
        with self.settings(BRIDGE_LOGIN_WINDOW=1):
            loader = BridgeChecker(BridgeWorker())
            bri_acc = loader.get_bridge().get_user_by_uwnetid('alumni')
            self.assertTrue(loader.not_accessed(bri_acc))
            bri_acc.logged_in_at = get_now() - timedelta(days=1)
            self.assertFalse(loader.not_accessed(bri_acc))
            bri_acc.logged_in_at = None
            self.assertTrue(loader.not_accessed(bri_acc))

    def test_load(self):
        with self.settings(BRIDGE_LOGIN_WINDOW=0):
            loader = BridgeChecker(BridgeWorker())
            set_db_records()
            loader.load()

            alumni = get_by_netid('alumni')
            self.assertEqual(alumni.bridge_id, 199)
            self.assertEqual(loader.get_total_count(), 8)
            self.assertEqual(loader.get_total_checked_users(), 6)
            self.assertEqual(loader.get_new_user_count(), 0)
            self.assertEqual(loader.get_netid_changed_count(), 2)
            self.assertEqual(loader.get_deleted_count(), 1)
            self.assertEqual(loader.get_restored_count(), 0)
            self.assertEqual(loader.get_updated_count(), 4)
            self.assertEqual(loader.get_error_report(), "")
            self.assertFalse(loader.has_error())
