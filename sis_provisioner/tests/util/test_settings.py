from django.test import TestCase
from django.conf import settings
from sis_provisioner.util.settings import (
    errors_to_abort_loader, get_csv_file_path_prefix, get_csv_file_size,
    get_csv_file_name_prefix, get_total_work_positions_to_load)

CSV_ROOT = "/tmp/fl_test"


class TestSetting(TestCase):

    def test_default(self):
        with self.settings(ERRORS_TO_ABORT_LOADER=[400]):
            errors = errors_to_abort_loader()
            self.assertEqual(len(errors), 1)
            self.assertEqual(errors[0], 400)

    def test_get_file_path_prefix(self):
        with self.settings(BRIDGE_IMPORT_CSV_ROOT=CSV_ROOT):
            self.assertEqual(get_csv_file_path_prefix(), CSV_ROOT)

    def test_get_csv_file_name_prefix(self):
        with self.settings(BRIDGE_IMPORT_USER_FILENAME='usr'):
            self.assertEqual(get_csv_file_name_prefix(), 'usr')

    def test_get_csv_file_size(self):
        with self.settings(BRIDGE_IMPORT_USER_FILE_SIZE=10):
            self.assertEqual(get_csv_file_size(), 10)

    def test_get_total_worker_positions_to_load(self):
        with self.settings(BRIDGE_USER_WORK_POSITIONS=1):
            self.assertEqual(get_total_work_positions_to_load(), 1)
