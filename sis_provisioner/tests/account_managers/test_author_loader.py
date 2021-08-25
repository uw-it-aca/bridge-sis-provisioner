# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TransactionTestCase
from sis_provisioner.account_managers.author_loader import AuthorChecker
from sis_provisioner.account_managers.bridge_worker import BridgeWorker
from sis_provisioner.tests import (
    fdao_gws_override, fdao_pws_override, fdao_bridge_override)
from sis_provisioner.tests.dao import get_mock_bridge_user
from sis_provisioner.tests.account_managers import (
    set_db_records, set_db_err_records)


@fdao_bridge_override
@fdao_gws_override
@fdao_pws_override
class TestBridgeUserChecker(TransactionTestCase):

    def test_fetch_users(self):
        loader = AuthorChecker(BridgeWorker())
        bridge_users = loader.fetch_users()
        self.assertEqual(len(bridge_users), 2)
        self.assertEqual(len(loader.cur_author_set), 5)

    def test_add_author_role(self):
        set_db_records()
        loader = AuthorChecker(BridgeWorker())
        loader.add_author_role("javerage")
        self.assertEqual(loader.get_updated_count(), 1)
        self.assertFalse(loader.has_error())

        # 500 Error
        set_db_err_records()
        loader.add_author_role("error500")
        self.assertTrue(loader.has_error())

        # not in PWS
        loader = AuthorChecker(BridgeWorker())
        loader.add_author_role("not_in_pws")
        self.assertFalse(loader.has_error())

    def test_remove_author_role(self):
        set_db_records()
        loader = AuthorChecker(BridgeWorker())
        retiree = loader.get_bridge().get_user_by_uwnetid('retiree')
        loader.remove_author_role(retiree)
        self.assertEqual(loader.get_updated_count(), 1)
        self.assertFalse(loader.has_error())

    def test_load(self):
        set_db_records()
        set_db_err_records()
        loader = AuthorChecker(BridgeWorker())
        loader.load()
        self.assertEqual(loader.get_updated_count(), 2)
