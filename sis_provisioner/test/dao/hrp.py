from django.test import TestCase
from restclients.exceptions import DataFailureException
from sis_provisioner.test import fdao_hrp_override, fdao_pws_override
from sis_provisioner.dao.pws import get_person
from sis_provisioner.dao.hrp import get_appointee, get_appointments


@fdao_hrp_override
@fdao_pws_override
class TestHrpDao(TestCase):

    def test_get_appointee(self):
        person = get_person('staff')
        self.assertIsNotNone(person)
        appointee = get_appointee(person)
        self.assertEqual(appointee.employee_id,
                         '100000001')

    def test_get_appointments(self):
        person = get_person('staff')
        apps = get_appointments(person)
        self.assertIsNotNone(apps)
        self.assertEqual(len(apps), 0)

        person = get_person('faculty')
        apps = get_appointments(person)
        self.assertIsNotNone(apps)
        self.assertEqual(len(apps), 1)

        person = get_person('botgrad')
        apps = get_appointments(person)
        self.assertIsNotNone(apps)
        self.assertEqual(len(apps), 3)
        self.assertEqual(apps[0].app_number, 1)
        self.assertEqual(apps[0].job_class_code, "7777")
        self.assertEqual(apps[0].org_code, "5200005000")
        self.assertEqual(apps[1].app_number, 2)
        self.assertEqual(apps[1].job_class_code, "7940")
        self.assertEqual(apps[1].org_code, "5200005000")
        self.assertEqual(apps[2].app_number, 3)
        self.assertEqual(apps[2].job_class_code, "7926")
        self.assertEqual(apps[2].org_code, "5100001000")

    def test_none_appointee(self):
        person = get_person('retiree')
        self.assertIsNotNone(person)
        appointee = get_appointee(person)
        self.assertIsNone(appointee)
