from django.test import TransactionTestCase
from sis_provisioner.account_managers.bridge_worker import BridgeWorker
from sis_provisioner.account_managers.customgrp_bridge import CustomGroupLoader
from sis_provisioner.tests import fdao_gws_override

@fdao_gws_override
class TestCustomGroupLoader(TransactionTestCase):

    def test_fetch_users(self):
        loader = CustomGroupLoader(BridgeWorker())
        user_list = loader.fetch_users()
        self.assertEqual(len(user_list), 1)
        self.assertEqual(user_list, ['not_in_pws'])