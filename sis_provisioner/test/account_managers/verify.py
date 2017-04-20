from django.conf import settings
from django.test import TransactionTestCase
from datetime import timedelta
from sis_provisioner.test import fdao_bridge_override
from sis_provisioner.dao.user import get_user_by_netid
from sis_provisioner.models import UwBridgeUser, get_now
from sis_provisioner.account_managers.verify import set_bridge_ids


@fdao_bridge_override
class TestUserVerifier(TransactionTestCase):

    def test_set_bridge_ids_for_existing_users(self):
        self.assertEqual(set_bridge_ids(), 0)

        UwBridgeUser(netid='javerage',
                     regid='9136CCB8F66711D5BE060004AC494FFE',
                     last_visited_at=get_now(),
                     email='javerage@uw.edu',
                     first_name='James',
                     last_name='Average').save()

        UwBridgeUser(netid='leftuw',
                     regid="B814EFBC6A7C11D5A4AE0004AC494FFE",
                     last_visited_at=get_now(),
                     email='leftuw@uw.edu',
                     first_name='Left',
                     last_name='UW').save()

        UwBridgeUser(netid='staff',
                     regid="10000000000000000000000000000001",
                     bridge_id=197,
                     last_visited_at=get_now(),
                     email='staff@uw.edu',
                     first_name='Staff',
                     last_name='UW',
                     action_priority=1).save()

        UwBridgeUser(netid='toremove',
                     regid='10000000000000000000000000000000',
                     last_visited_at=get_now(),
                     email='toremove@uw.edu',
                     first_name='Not In',
                     last_name='Bridge').save()

        self.assertEqual(set_bridge_ids(), 3)

        user = get_user_by_netid('javerage')
        self.assertEqual(user.bridge_id, 195)

        user1 = get_user_by_netid('leftuw')
        self.assertEqual(user1.bridge_id, 200)

        user2 = get_user_by_netid('staff')
        self.assertEqual(user2.bridge_id, 196)
