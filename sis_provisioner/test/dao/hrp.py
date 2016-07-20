from django.test import TestCase
from restclients.exceptions import DataFailureException
from sis_provisioner.test import FHRP, FPWS
from sis_provisioner.dao.pws import get_person
from sis_provisioner.dao.hrp import get_appointee


class TestHrpDao(TestCase):

    def test_get_person(self):
        with self.settings(RESTCLIENTS_PWS_DAO_CLASS=FPWS,
                           RESTCLIENTS_HRPWS_DAO_CLASS=FHRP):
            person = get_person('staff')
            self.assertIsNotNone(person)
            appointee = get_appointee(person)
            self.assertEqual(appointee.employee_id,
                             '100000001')
            self.assertEqual(appointee.status, 'S')
            self.assertEqual(appointee.home_dept_org_code,
                             '2070001000')
