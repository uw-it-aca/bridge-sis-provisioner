# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.conf import settings
from django.core.files.storage import default_storage
from django.test import TransactionTestCase
from django.test.utils import override_settings
from sis_provisioner.csv.user_writer import (
    get_user_file_name, make_import_user_csv_files)
from sis_provisioner.dao.uw_account import get_all_uw_accounts
from sis_provisioner.tests.csv import (
    user_file_name_override, fdao_pws_override, fdao_hrp_override)
from sis_provisioner.tests.account_managers import set_db_records


override_bridge = override_settings(BRIDGE_USER_WORK_POSITIONS=2)


@fdao_pws_override
@fdao_hrp_override
@user_file_name_override
@override_bridge
class TestUserWriter(TransactionTestCase):

    def test_get_file_name_prefix(self):
        with self.settings(BRIDGE_IMPORT_USER_FILENAME="blah"):
            self.assertEqual(get_user_file_name("/tmp", 1),
                             "/tmp/blah1.csv")
            self.assertEqual(get_user_file_name("/tmp", 2),
                             "/tmp/blah2.csv")

    def test_make_import_user_csv_files(self):
        with self.settings(BRIDGE_IMPORT_USER_FILENAME="blah",
                           BRIDGE_IMPORT_USER_FILE_SIZE=1):
            file_path = ""
            user_number = make_import_user_csv_files(None,
                                                     file_path)
            self.assertEqual(user_number, 0)
            set_db_records()
            user_number = make_import_user_csv_files(get_all_uw_accounts(),
                                                     file_path)

            self.assertEqual(user_number, 2)
            self.verify_file_content("blah1.csv", "Library")
            self.verify_file_content("blah2.csv", "UW Benefits Office")

    def verify_file_content(self, fp, home_dept):
        try:
            fo = default_storage.open(fp, mode="r")
            result = fo.read()
            self.assertTrue(home_dept in result)
        finally:
            default_storage.delete(fp)
            self.assertFalse(default_storage.exists(fp))
