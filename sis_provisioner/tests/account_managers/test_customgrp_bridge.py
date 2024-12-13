# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TransactionTestCase
from sis_provisioner.account_managers.bridge_worker import BridgeWorker
from sis_provisioner.account_managers.customgrp_bridge import CustomGroupLoader
from sis_provisioner.tests import fdao_gws_override


@fdao_gws_override
class TestCustomGroupLoader(TransactionTestCase):

    def test_fetch_users(self):
        loader = CustomGroupLoader(BridgeWorker())
        self.assertFalse(loader.update_existing_accs())
        user_list = loader.fetch_users()
        self.assertEqual(len(user_list), 0)
