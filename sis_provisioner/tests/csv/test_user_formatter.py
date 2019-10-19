from django.conf import settings
from django.test import TransactionTestCase
from django.test.utils import override_settings
from sis_provisioner.csv.user_formatter import get_headers, get_attr_list
from sis_provisioner.dao.pws import get_person
from sis_provisioner.dao.hrp import get_worker
from sis_provisioner.tests.csv import fdao_pws_override, fdao_hrp_override
from sis_provisioner.tests.account_managers import set_db_records


override_bridge = override_settings(BRIDGE_USER_WORK_POSITIONS=2)


@fdao_pws_override
@fdao_hrp_override
@override_bridge
class TestUserFormatter(TransactionTestCase):

    def test_get_headers(self):
        headers = get_headers()
        self.assertEqual(len(headers), 25)
        self.assertEqual(headers[0], 'UNIQUE ID')
        self.assertEqual(headers[1], 'email')
        self.assertEqual(headers[2], 'full_name')
        self.assertEqual(headers[3], 'first_name')
        self.assertEqual(headers[4], 'last_name')
        self.assertEqual(headers[5], 'regid')
        self.assertEqual(headers[6], 'employee_id')
        self.assertEqual(headers[7], 'student_id')
        self.assertEqual(headers[8], 'job_title')
        self.assertEqual(headers[9], 'manager_id')
        self.assertEqual(headers[10], 'department')
        self.assertEqual(headers[11], 'pos1_budget_code')
        self.assertEqual(headers[12], 'pos1_job_class')
        self.assertEqual(headers[13], 'pos1_job_code')
        self.assertEqual(headers[14], 'pos1_location')
        self.assertEqual(headers[15], 'pos1_org_code')
        self.assertEqual(headers[16], 'pos1_org_name')
        self.assertEqual(headers[17], 'pos1_unit_code')
        self.assertEqual(headers[18], 'pos2_budget_code')
        self.assertEqual(headers[19], 'pos2_job_class')
        self.assertEqual(headers[20], 'pos2_job_code')
        self.assertEqual(headers[21], 'pos2_location')
        self.assertEqual(headers[22], 'pos2_org_code')
        self.assertEqual(headers[23], 'pos2_org_name')
        self.assertEqual(headers[24], 'pos2_unit_code')

    def test_get_attr_list_withhrp(self):
        set_db_records()
        person = get_person('faculty')
        worker = get_worker(person)

        user_attr_list = get_attr_list(person, worker)
        self.assertEqual(len(user_attr_list), 25)
        self.assertEqual(user_attr_list[0], "faculty@uw.edu")
        self.assertEqual(user_attr_list[1], "faculty@uw.edu")
        self.assertEqual(user_attr_list[2], "William E Faculty")
        self.assertEqual(user_attr_list[3], "William E")
        self.assertEqual(user_attr_list[4], "Faculty")
        self.assertEqual(user_attr_list[5], "10000000000000000000000000000005")
        self.assertEqual(user_attr_list[6], "000000005")
        self.assertEqual(user_attr_list[7], "0000005")
        self.assertEqual(user_attr_list[8], "Clinical Associate Professor")
        self.assertEqual(user_attr_list[9], 196)
        self.assertEqual(user_attr_list[10], "Family Medicine")
        self.assertEqual(user_attr_list[11], "3040111000")
        self.assertEqual(user_attr_list[12], "Academic Personnel")
        self.assertEqual(user_attr_list[13], "21184")
        self.assertEqual(user_attr_list[14], "Seattle Campus")
        self.assertEqual(user_attr_list[15], "SOM:")
        self.assertEqual(user_attr_list[16],
                         "Family Medicine: Volunteer JM Academic")
        self.assertEqual(user_attr_list[17], "00753")
        self.assertIsNone(user_attr_list[18])
        self.assertIsNone(user_attr_list[19])
        self.assertIsNone(user_attr_list[20])
        self.assertIsNone(user_attr_list[21])
        self.assertIsNone(user_attr_list[22])
        self.assertIsNone(user_attr_list[23])
        self.assertIsNone(user_attr_list[24])
