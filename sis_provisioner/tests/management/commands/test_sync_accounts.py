import time
from django.test import TransactionTestCase
from unittest.mock import patch
from django.core.management import call_command
from sis_provisioner.account_managers.gws_bridge import GwsBridgeLoader
from sis_provisioner.tests import (
    fdao_gws_override, fdao_pws_override, fdao_bridge_override)
from sis_provisioner.tests.account_managers import set_db_records


users = ['affiemp', 'error500', 'faculty', 'javerage',
         'not_in_pws', 'retiree', 'staff']


@fdao_gws_override
@fdao_pws_override
@fdao_bridge_override
class TestLoadUserViaBridgeApi(TransactionTestCase):

    @patch.object(GwsBridgeLoader, 'fetch_users',
                  return_value=users, spec=True)
    def test_load_from_gws_to_bridge(self, mock_fn):
        with self.settings(BRIDGE_GWS_CACHE='/tmp/gwsusermc'):
            set_db_records()
            call_command('sync_accounts', 'gws')

    def test_load_from_dbemp_to_bridge(self):
        time.sleep(1)
        set_db_records()
        call_command('sync_accounts', 'customg')

    def test_load_from_dbemp_to_bridge(self):
        time.sleep(1)
        set_db_records()
        call_command('sync_accounts', 'db-emp')

    def test_load_from_dbother_to_bridge(self):
        time.sleep(1)
        set_db_records()
        call_command('sync_accounts', 'db-other')

    def test_load_bridge_to_db(self):
        time.sleep(2)
        set_db_records()
        call_command('sync_accounts', 'bridge')

    def test_load_pws_bridge(self):
        time.sleep(2)
        set_db_records()
        call_command('sync_accounts', 'pws')

    def test_load_hrp_bridge(self):
        time.sleep(2)
        set_db_records()
        call_command('sync_accounts', 'hrp')
