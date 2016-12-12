import time
from django.test import TransactionTestCase
from django.core.management import call_command
from sis_provisioner.test import fdao_gws_override, fdao_pws_override,\
    fdao_bridge_override


@fdao_gws_override
@fdao_pws_override
@fdao_bridge_override
class TestLoadUserViaBridgeApi(TransactionTestCase):

    def test_load_from_gws(self):
        call_command('load_user_to_bridge', 'gws')

    def test_load_from_db(self):
        time.sleep(1)
        call_command('load_user_to_bridge', 'db')

    def test_load_from_bridge(self):
        time.sleep(2)
        call_command('load_user_to_bridge', 'bridge')

    def test_reload(self):
        time.sleep(3)
        call_command('load_user_to_bridge', 'rerun')
