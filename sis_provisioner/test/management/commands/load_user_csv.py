import time
from django.test import TransactionTestCase
from django.core.management import call_command
from sis_provisioner.test import fdao_gws_override, fdao_pws_override,\
    fdao_bridge_override


@fdao_gws_override
@fdao_pws_override
@fdao_bridge_override
class TestLoadUserViaCsv(TransactionTestCase):

    def test_load_from_gws(self):
        call_command('load_user_csv', 'gws')

    def test_load_from_db(self):
        time.sleep(2)
        call_command('load_user_csv', 'db')

    def test_load_from_bridge(self):
        time.sleep(4)
        call_command('load_user_csv', 'bridge')
