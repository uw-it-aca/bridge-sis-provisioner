import os
from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings
from sis_provisioner.models import BridgeUser, get_now
from sis_provisioner.csv.user_writer import _get_file_name_prefix,\
    _get_file_size, get_user_file_name, make_import_user_csv_files,\
    get_delete_user_file_name, make_delete_user_csv_file,\
    get_netid_changed_file_name, get_regid_changed_file_name,\
    make_import_netid_changed_user_csv_file,\
    make_import_regid_changed_user_csv_file,\
    make_key_changed_user_csv_files


def get_users(size=1):
    users = []
    i = 0
    while i < size:
        users.append(BridgeUser(regid="11111111111111111111111111111111",
                                netid="dummy",
                                last_visited_date=get_now(),
                                last_name="Dummy"))
        i += 1
    return users


class TestUserWriter(TestCase):

    def test_get_file_name_prefix(self):
        with self.settings(BRIDGE_IMPORT_USER_FILENAME="blah"):
            self.assertEqual(_get_file_name_prefix(), "blah")

    def test_get_file_size(self):
        with self.settings(BRIDGE_IMPORT_USER_FILE_SIZE=5):
            self.assertEqual(_get_file_size(), 5)

    def test_get_file_name_prefix(self):
        with self.settings(BRIDGE_IMPORT_USER_FILENAME="blah"):
            self.assertEqual(get_user_file_name("/tmp", 1), "/tmp/blah1.csv")
            self.assertEqual(get_user_file_name("/tmp", 2), "/tmp/blah2.csv")

    def test_make_import_user_csv_files(self):
        with self.settings(BRIDGE_IMPORT_USER_FILENAME="blah",
                           BRIDGE_IMPORT_USER_FILE_SIZE=1):
            file_path = "/tmp"
            user_number = make_import_user_csv_files(get_users(3),
                                                     file_path,
                                                     False)
            self.assertEqual(user_number, 3)
            self.verify_file_content("/tmp/blah1.csv", False)
            self.verify_file_content("/tmp/blah2.csv", False)
            self.verify_file_content("/tmp/blah3.csv", False)

    def test_get_delete_user_file_name(self):
        file_path = "/tmp"
        self.assertEqual(get_delete_user_file_name(file_path),
                         "/tmp/users_delete.csv")

    def test_get_netid_changed_file_name(self):
        file_path = "/tmp"
        self.assertEqual(get_netid_changed_file_name(file_path),
                         "/tmp/users_netid_changed.csv")

    def test_get_regid_changed_file_name(self):
        file_path = "/tmp"
        self.assertEqual(get_regid_changed_file_name(file_path),
                         "/tmp/users_regid_changed.csv")

    def test_make_delete_user_csv_file(self):
        netids = ['abc', 'cde', 'efg']
        file_path = "/tmp"
        user_number = make_delete_user_csv_file(netids, file_path)
        self.assertEqual(user_number, 3)
        fp = "/tmp/users_delete.csv"
        self.assertTrue(os.path.exists(fp))
        result = open(fp).read()
        try:
            self.assertEqual(
                result,
                "UNIQUE ID\nabc@uw.edu\ncde@uw.edu\nefg@uw.edu\n")
        finally:
            os.remove(fp)

    def test_make_key_changed_user_csv_files_hrp(self):
        fp = "/tmp/users_xx_changed.csv"
        user_number = make_key_changed_user_csv_files(
            get_users(), fp, include_hrp=True)
        self.assertEqual(user_number, 1)
        self.verify_file_content(fp, True)

    def test_make_key_changed_user_csv_files(self):
        fp = "/tmp/users_xxx_changed.csv"
        user_number = make_key_changed_user_csv_files(
            get_users(), fp, include_hrp=False)
        self.assertEqual(user_number, 1)
        self.verify_file_content(fp)

    def test_make_import_netid_changed_user_csv_file(self):
        user_number = make_import_netid_changed_user_csv_file(
            get_users(), "/tmp", include_hrp=False)
        self.assertEqual(user_number, 1)
        self.verify_file_content("/tmp/users_netid_changed.csv")

    def test_make_import_regid_changed_user_csv_file(self):
        user_number = make_import_regid_changed_user_csv_file(
            get_users(), "/tmp", include_hrp=False)
        self.assertEqual(user_number, 1)
        self.verify_file_content("/tmp/users_regid_changed.csv")

    def verify_file_content(self, fp, has_hrp_attrs=False):
        self.assertTrue(os.path.exists(fp))
        if has_hrp_attrs:
            expected = ('UNIQUE ID,NAME,EMAIL,regid' +
                        ',emp campus 1,emp coll 1,emp dept 1' +
                        ',emp campus 2,emp coll 2,emp dept 2' +
                        ',emp campus 3,emp coll 3,emp dept 3\n' +
                        'dummy@uw.edu,Dummy,dummy@uw.edu,' +
                        '11111111111111111111111111111111,,,,,,,,,\n')
        else:
            expected = ('UNIQUE ID,NAME,EMAIL,regid\n' +
                        'dummy@uw.edu,Dummy,dummy@uw.edu,' +
                        '11111111111111111111111111111111\n')
        try:
            fo = open(fp)
            result = fo.read()
            # print "%s====%s====%s" % (fp, has_hrp_attrs, result)
            self.assertEqual(result, expected)
        finally:
            os.remove(fp)
            self.assertFalse(os.path.exists(fp))
