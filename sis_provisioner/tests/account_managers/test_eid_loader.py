import logging
from datetime import timedelta
from django.test import TransactionTestCase
from sis_provisioner.dao.uw_account import get_by_employee_id
from sis_provisioner.account_managers.eid_loader import load
from sis_provisioner.tests import fdao_pws_override
from sis_provisioner.tests.account_managers import set_db_records


@fdao_pws_override
class TestEidLoader(TransactionTestCase):

    def test_load(self):
        set_db_records()
        self.assertEqual(load(), 3)
        self.assertEqual(get_by_employee_id("123456789").netid, "javerage")
        self.assertEqual(get_by_employee_id("100000001").netid, "staff")
        self.assertEqual(get_by_employee_id("000000005").netid, "tyler")
