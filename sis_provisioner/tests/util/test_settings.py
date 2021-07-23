# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase
from django.conf import settings
from sis_provisioner.util.settings import (
    errors_to_abort_loader, get_csv_file_path_prefix, get_csv_file_size,
    get_csv_file_name_prefix, get_total_work_positions_to_load,
    get_author_group_name, get_login_window, get_person_changed_window,
    get_worker_changed_window, get_group_member_add_window,
    get_group_member_del_window, check_all_accounts)

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

    def test_get_author_group_name(self):
        with self.settings(BRIDGE_AUTHOR_GROUP_NAME='a'):
            self.assertEqual(get_author_group_name(), 'a')

    def test_get_login_window(self):
        with self.settings(BRIDGE_LOGIN_WINDOW=1):
            self.assertEqual(get_login_window(), 1)

    def test_get_person_changed_window(self):
        with self.settings(BRIDGE_PERSON_CHANGE_WINDOW=60):
            self.assertEqual(get_person_changed_window(), 60)

    def test_get_worker_changed_window(self):
        with self.settings(BRIDGE_WORKER_CHANGE_WINDOW=60):
            self.assertEqual(get_worker_changed_window(), 60)

    def test_get_group_member_add_window(self):
        with self.settings(BRIDGE_GMEMBER_ADD_WINDOW=10):
            self.assertEqual(get_group_member_add_window(), 10)

    def test_get_group_member_del_window(self):
        with self.settings(BRIDGE_GMEMBER_DEL_WINDOW=8):
            self.assertEqual(get_group_member_del_window(), 8)

    def test_get_group_member_del_window(self):
        self.assertFalse(check_all_accounts())
        with self.settings(BRIDGE_CHECK_ALL_ACCOUNTS=True):
            self.assertTrue(check_all_accounts())
