# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import re
from django.test import TestCase
from django.core.files.storage import default_storage
from sis_provisioner.csv import get_aline_csv, open_file, get_filepath


class TestCsvInit(TestCase):

    def test_open_file(self):
        file_path = "blah1.csv"
        expected = "Mary had a little lamb.\n"
        fh = open_file(file_path)
        self.assertIsNotNone(fh)
        fh.write(expected)
        fh.close()
        self.assertTrue(default_storage.exists(file_path))
        fh = default_storage.open(file_path)
        result = fh.read()
        try:
            self.assertEqual(result.decode("utf-8"), expected)
        finally:
            fh.close()
            default_storage.delete(file_path)

    def test_get_filepath(self):
        fp = get_filepath()
        self.assertTrue(re.match(r"^\d{8}-\d{6}-\d{6}$", fp))
        self.assertFalse(default_storage.exists(fp))

    def test_get_aline_csv(self):
        self.assertEqual(get_aline_csv(["UNIQUE ID"]),
                         "UNIQUE ID\n")
        self.assertEqual(get_aline_csv(["UNIQUE ID", "Email", "Name"]),
                         "UNIQUE ID,Email,Name\n")
