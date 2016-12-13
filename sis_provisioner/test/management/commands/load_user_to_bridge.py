import time
from django.test import TransactionTestCase
from django.core.management import call_command
from sis_provisioner.test import fdao_gws_override, fdao_pws_override,\
    fdao_bridge_override


@fdao_gws_override
@fdao_pws_override
@fdao_bridge_override
class TestLoadUserViaBridgeApi(TransactionTestCase):

    def test_load_to_bridge(self):
        call_command('load_user_to_bridge', 'gws')

        time.sleep(1)
        call_command('load_user_to_bridge', 'db')

        time.sleep(2)
        call_command('load_user_to_bridge', 'bridge')

        time.sleep(3)
        call_command('load_user_to_bridge', 'rerun')
