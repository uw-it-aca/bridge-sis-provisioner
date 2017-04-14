import time
from django.test import TransactionTestCase
from django.core.management import call_command
from sis_provisioner.test import fdao_pws_override, fdao_bridge_override,\
    mock_uw_bridge_user


@fdao_pws_override
@fdao_bridge_override
class TestClearDbRecord(TransactionTestCase):

    def test_clear_by_regid(self):
        user, person = mock_uw_bridge_user('staff')
        user.regid = '10000000000000000000000000000006'
        user.save()
        call_command('clear_db_record',
                     '10000000000000000000000000000006',
                     '')

    def test_clear_by_netid(self):
        user, person = mock_uw_bridge_user('staff')
        user.netid = 'changed'
        user.save()
        call_command('clear_db_record',
                     '',
                     'changed')

    def test_clear_error(self):
        call_command('clear_db_record',
                     '',
                     'staff')
        call_command('clear_db_record',
                     '10000000000000000000000000000006',
                     '')
