from django.conf import settings
from django.test import TransactionTestCase
from django.test.utils import override_settings
from sis_provisioner.csv.user_formatter import HEADERS, get_attr_list
from sis_provisioner.dao.pws import get_person
from sis_provisioner.dao.hrp import get_worker
from sis_provisioner.tests.csv import fdao_pws_override, fdao_hrp_override
from sis_provisioner.tests.account_managers import set_db_records


@fdao_pws_override
@fdao_hrp_override
class TestUserFormatter(TransactionTestCase):

    def setup(self):
        self.maxDiff = None

    def test_get_headers(self):
        headers = HEADERS
        self.assertEqual(len(headers), 17)

    def test_get_attr_list_withhrp(self):
        set_db_records()
        person = get_person('faculty')
        worker = get_worker(person)

        user_attr_list = get_attr_list(person, worker)
        self.assertEqual(len(user_attr_list), 17)
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
        self.assertEqual(user_attr_list[14], "SOM:")
        self.assertEqual(user_attr_list[15],
                         "Family Medicine: Volunteer JM Academic")
        self.assertEqual(user_attr_list[16], "00753")
