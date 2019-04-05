from datetime import timedelta
from django.test import TransactionTestCase
from django.core.management import call_command
from sis_provisioner.models import UwBridgeUser, UwAccount, get_now
from sis_provisioner.tests import fdao_pws_override


@fdao_pws_override
class TestLoadUserViaBridgeApi(TransactionTestCase):

    def test_load_from_gws_to_bridge(self):
        javerage = UwBridgeUser.objects.create(
            netid='javerage',
            bridge_id=195,
            regid="9136CCB8F66711D5BE060004AC494FFE",
            last_name="Student",
            last_visited_at=get_now())
        ellen = UwBridgeUser.objects.create(
            netid='ellen',
            bridge_id=194,
            regid="10000000000000000000000000000000",
            last_name="Retiree",
            last_visited_at=get_now())
        retiree = UwBridgeUser.objects.create(
            netid='retiree',
            bridge_id=204,
            regid="10000000000000000000000000000006",
            last_name="Retiree",
            last_visited_at=get_now())
        tyler = UwBridgeUser.objects.create(
            netid='tyler',
            bridge_id=198,
            regid="10000000000000000000000000000005",
            last_name="Faculty",
            last_visited_at=get_now())
        leftuw = UwBridgeUser.objects.create(
            netid='leftuw',
            bridge_id=200,
            regid="56229F4D3B504559AF23956737A3CF9D",
            last_name="UW",
            last_visited_at=get_now())
        staff = UwBridgeUser.objects.create(
            netid='staff',
            bridge_id=196,
            regid="10000000000000000000000000000001",
            last_name="Staff",
            disabled=True,
            last_visited_at=get_now() - timedelta(days=22))

        call_command('migrate_table')
        staff1 = UwAccount.get("staff")
        self.assertTrue(staff1.disabled)
        self.assertEqual(staff1.bridge_id, 196)
        self.assertEqual(UwAccount.get("leftuw").bridge_id, 200)
        self.assertEqual(UwAccount.get("tyler").bridge_id, 198)
        self.assertEqual(UwAccount.get("retiree").bridge_id, 204)
        self.assertEqual(UwAccount.get("ellen").bridge_id, 194)
        self.assertEqual(UwAccount.get("javerage").bridge_id, 195)
