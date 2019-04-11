from django.test import TransactionTestCase
from sis_provisioner.models import UwAccount, get_now
from sis_provisioner.dao import DataFailureException
from sis_provisioner.dao.pws import get_person
from sis_provisioner.dao.uw_account import (
    delete_uw_account, get_all_uw_accounts, get_by_bridgeid,
    get_by_netid, save_uw_account, set_bridge_id)
from sis_provisioner.tests import fdao_pws_override


@fdao_pws_override
class TestUwAccountDao(TransactionTestCase):

    def mock_uw_account(self, uwnetid):
        return UwAccount.objects.create(netid=uwnetid,
                                        last_updated=get_now())

    def test_get_all_uw_accounts(self):
        self.assertEqual(len(get_all_uw_accounts()), 0)

        user1 = self.mock_uw_account('staff')
        user2 = self.mock_uw_account('faculty')

        users = get_all_uw_accounts()
        self.assertEqual(len(users), 2)

    def test_get_by_ids(self):
        user = self.mock_uw_account('staff')
        user.bridge_id = 100
        user.save()

        result_set = get_by_bridgeid(100)
        self.assertEqual(len(result_set), 1)
        self.assertEqual(result_set[0].bridge_id, 100)
        self.assertEqual(result_set[0].netid, 'staff')

        user1 = get_by_netid('staff')
        self.assertEqual(user, user1)

        delete_uw_account('staff')
        self.assertIsNone(get_by_netid('staff'))

        self.assertIsNone(get_by_bridgeid(0))
        self.assertEqual(len(get_by_bridgeid(12)), 0)
        self.assertIsNone(get_by_netid('none'))

    def test_save_new_uw_account(self):
        affiemp = person = get_person('affiemp')
        acc = save_uw_account(affiemp)
        self.assertEqual(acc.netid, 'affiemp')
        self.assertFalse(acc.has_prev_netid())
        self.assertEqual(len(get_all_uw_accounts()), 1)

    def test_save_uw_account(self):
        acc1 = self.mock_uw_account('tyler')
        self.assertEqual(len(get_all_uw_accounts()), 1)

        person = get_person('faculty')
        acc = save_uw_account(person)
        self.assertEqual(acc.netid, person.uwnetid)
        self.assertTrue(acc.has_prev_netid())
        self.assertEqual(acc.prev_netid, 'tyler')
        self.assertEqual(len(get_all_uw_accounts()), 1)

        self.assertTrue(set_bridge_id('faculty', 100))
        self.assertFalse(set_bridge_id('none', 100))

    def test_save_uw_accounts(self):
        # test a user with multiple accounts
        acc1 = self.mock_uw_account('ellen')
        acc2 = self.mock_uw_account('retiree')
        self.assertEqual(len(get_all_uw_accounts()), 2)
        person = get_person('retiree')
        acc = save_uw_account(person)
        self.assertEqual(acc.netid, person.uwnetid)
        self.assertEqual(acc.prev_netid, 'ellen')
        self.assertEqual(len(get_all_uw_accounts()), 1)
