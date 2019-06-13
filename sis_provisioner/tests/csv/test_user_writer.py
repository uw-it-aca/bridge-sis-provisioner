import os
from django.conf import settings
from django.test import TestCase
from sis_provisioner.csv.user_writer import (
    _get_file_name_prefix, _get_file_size, get_user_file_name,
    make_import_user_csv_files)
from sis_provisioner.dao.uw_account import get_all_uw_accounts
from sis_provisioner.tests.csv import (
    user_file_name_override, fdao_pws_override, fdao_hrp_override)
from sis_provisioner.tests.account_managers import set_db_records


@fdao_pws_override
@fdao_hrp_override
@user_file_name_override
class TestUserWriter(TestCase):

    def test_get_file_name_prefix(self):
        with self.settings(BRIDGE_IMPORT_USER_FILENAME="blah"):
            self.assertEqual(_get_file_name_prefix(), "blah")

    def test_get_file_size(self):
        with self.settings(BRIDGE_IMPORT_USER_FILE_SIZE=5):
            self.assertEqual(_get_file_size(), 5)

    def test_get_file_name_prefix(self):
        with self.settings(BRIDGE_IMPORT_USER_FILENAME="blah"):
            self.assertEqual(get_user_file_name("/tmp", 1),
                             "/tmp/blah1.csv")
            self.assertEqual(get_user_file_name("/tmp", 2),
                             "/tmp/blah2.csv")

    def test_make_import_user_csv_files(self):
        with self.settings(BRIDGE_IMPORT_USER_FILENAME="blah",
                           BRIDGE_IMPORT_USER_FILE_SIZE=2):
            file_path = "/tmp"
            user_number = make_import_user_csv_files(None,
                                                     file_path)
            self.assertEqual(user_number, 0)
            set_db_records()
            user_number = make_import_user_csv_files(get_all_uw_accounts(),
                                                     file_path)

            self.assertEqual(user_number, 6)
            self.verify_file_content("/tmp/blah1.csv", 581)
            self.verify_file_content("/tmp/blah2.csv", 584)
            self.verify_file_content("/tmp/blah3.csv", 538)

    def verify_file_content(self, fp, length):
        try:
            fo = open(fp)
            result = fo.read()
            self.assertEqual(len(result), length)
        finally:
            os.remove(fp)
            self.assertFalse(os.path.exists(fp))
