import os
import re
import shutil
from django.conf import settings
from django.test import TransactionTestCase
from django.test.utils import override_settings
from sis_provisioner.csv.writer import _get_file_path_prefix,\
    get_file_path, CsvMaker
from sis_provisioner.tests.csv import (
    fdao_pws_override, fdao_hrp_override, set_db_records)


CSV_ROOT = "/tmp/fl_test"
PATTERN = CSV_ROOT + r"/[2-9]\d{7}-\d{6}"
override_csv_root = override_settings(BRIDGE_IMPORT_CSV_ROOT=CSV_ROOT)
USER_FILENAME = 'busrs'
override_user_filename = override_settings(
    BRIDGE_IMPORT_USER_FILENAME=USER_FILENAME)


@fdao_pws_override
@fdao_hrp_override
@override_csv_root
@override_user_filename
class TestCsvWriter(TransactionTestCase):

    def test_get_file_path_prefix(self):
        self.assertEqual(_get_file_path_prefix(), CSV_ROOT)

    def test_get_file_path(self):
        fp = get_file_path()
        self.assertIsNotNone(fp)
        self.assertTrue(re.match(PATTERN, fp))
        self.assertTrue(os.path.exists(fp))
        os.rmdir(fp)

    def test_get_file_path_exce(self):
        with self.settings(BRIDGE_IMPORT_CSV_ROOT="/usr"):
            self.assertRaises(OSError, get_file_path)

    def test_load_user_csv_file(self):
        with self.settings(BRIDGE_IMPORT_USER_FILE_SIZE=2):
            set_db_records()
            maker = CsvMaker()
            fp = maker.filepath
            self.assertTrue(re.match(PATTERN, fp))
            number_users_wrote = maker.load_files()
            self.assertEqual(number_users_wrote, 3)
            self.assertTrue(os.path.exists(fp + "/busrs1.csv"))
            self.assertTrue(os.path.exists(fp + "/busrs2.csv"))
            os.remove(fp + "/busrs1.csv")
            os.remove(fp + "/busrs2.csv")
            os.rmdir(fp)
