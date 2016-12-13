from django.conf import settings
from django.test import TransactionTestCase
from datetime import timedelta
from sis_provisioner.test import fdao_bridge_override
from sis_provisioner.models import UwBridgeUser, get_now
from sis_provisioner.account_managers.verify import set_bridge_ids


@fdao_bridge_override
class TestUserVerifier(TransactionTestCase):

    def test_set_bridge_ids_for_existing_users(self):
        self.assertEqual(set_bridge_ids(), 0)

        user = UwBridgeUser(netid='javerage',
                            regid='9136CCB8F66711D5BE060004AC494FFE',
                            last_visited_at=get_now(),
                            email='javerage@uw.edu',
                            first_name='James',
                            last_name='Changed')
        user.save()
        user1 = UwBridgeUser(netid='leftuw',
                             regid='...',
                             last_visited_at=get_now(),
                             email='leftuw@uw.edu',
                             first_name='Left',
                             last_name='UW')
        user1.save()

        self.assertEqual(set_bridge_ids(), 2)
