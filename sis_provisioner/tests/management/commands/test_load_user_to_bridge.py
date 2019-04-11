import time
from django.test import TransactionTestCase
from django.core.management import call_command
from sis_provisioner.tests import (
    fdao_gws_override, fdao_pws_override, fdao_bridge_override)
from sis_provisioner.tests.account_managers import set_db_records


@fdao_gws_override
@fdao_pws_override
@fdao_bridge_override
class TestLoadUserViaBridgeApi(TransactionTestCase):

    def test_load_from_gws_to_bridge(self):
        set_db_records()
        call_command('load_user_to_bridge', 'gws')

    def test_load_from_db_to_bridge(self):
        time.sleep(1)
        set_db_records()
        call_command('load_user_to_bridge', 'db')

    def test_load_bridge_to_db(self):
        time.sleep(2)
        set_db_records()
        call_command('load_user_to_bridge', 'bridge')
