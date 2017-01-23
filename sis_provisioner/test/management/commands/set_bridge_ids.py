import time
from django.test import TransactionTestCase
from django.core.management import call_command
from sis_provisioner.test import fdao_pws_override, fdao_bridge_override


@fdao_pws_override
@fdao_bridge_override
class TestSetBridgeIds(TransactionTestCase):

    def test_set_bridge_ids(self):
        call_command('set_bridge_ids', 'javerage')

        time.sleep(2)
        call_command('set_bridge_ids', 'ALL')
