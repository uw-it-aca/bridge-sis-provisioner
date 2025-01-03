# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import re
import os
from django.conf import settings
from django.test import TransactionTestCase
from django.test.utils import override_settings
from django.core.files.storage import default_storage
from sis_provisioner.csv.writer import get_filepath, CsvMaker
from sis_provisioner.tests.csv import (
    fdao_pws_override, fdao_hrp_override, set_db_records)


PATTERN = r"^\d{8}-\d{6}-\d{6}$"
USER_FILENAME = 'busrs'
override_user_filename = override_settings(
    BRIDGE_IMPORT_USER_FILENAME=USER_FILENAME)
override_bridge = override_settings(BRIDGE_USER_WORK_POSITIONS=2)


@fdao_pws_override
@fdao_hrp_override
@override_user_filename
@override_bridge
class TestCsvWriter(TransactionTestCase):

    def test_get_filepath(self):
        fp = get_filepath()
        self.assertIsNotNone(fp)
        self.assertTrue(re.match(PATTERN, fp))
        self.assertFalse(default_storage.exists(fp))
        default_storage.delete(fp)

    @override_settings(BRIDGE_IMPORT_USER_FILE_SIZE=3)
    def test_load_user_csv_file(self):
        set_db_records()
        maker = CsvMaker()
        maker.filepath = ""
        self.assertEqual(len(maker.fetch_users()), 8)

        number_users_wrote = maker.load_files()
        self.assertEqual(number_users_wrote, 4)
        self.assertTrue(
            default_storage.exists(os.path.join(maker.filepath, "busrs1.csv")))
        self.assertTrue(
            default_storage.exists(os.path.join(maker.filepath, "busrs2.csv")))
        default_storage.delete("busrs1.csv")
        default_storage.delete("busrs2.csv")
