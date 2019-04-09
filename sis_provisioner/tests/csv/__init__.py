import os
import re
from django.test import TestCase
from sis_provisioner.csv import get_aline_csv, open_file, get_filepath


class TestCsv(TestCase):

    def test_open_file(self):
        file_path = "/tmp/blah1.csv"
        expected = "Mary had a little lamb.\n"
        fh = open_file(file_path)
        self.assertIsNotNone(fh)
        fh.write(expected)
        fh.close()
        self.assertTrue(os.path.isfile(file_path))
        result = open(file_path).read()
        try:
            self.assertEqual(result, expected)
        finally:
            os.remove(file_path)

    def test_get_filepath(self):
        parent_path = "/tmp"
        fp = get_filepath(parent_path)
        self.assertTrue(re.match(r"/tmp/[2-9]\d{7}-\d{6}", fp))
        self.assertTrue(os.path.exists(fp))
        os.rmdir(fp)
        self.assertFalse(os.path.exists(fp))

    def test_get_aline_csv(self):
        self.assertEqual(get_aline_csv(["UNIQUE ID"]),
                         "UNIQUE ID\n")
        self.assertEqual(get_aline_csv(["UNIQUE ID", "Email", "Name"]),
                         "UNIQUE ID,Email,Name\n")
