import os
from django.conf import settings
from django.test import TestCase
from sis_provisioner.models import UwBridgeUser, get_now
from sis_provisioner.csv.user_writer import _get_file_name_prefix,\
    _get_file_size, get_user_file_name, make_import_user_csv_files,\
    get_delete_user_file_name, make_delete_user_csv_file,\
    get_netid_changed_file_name, get_regid_changed_file_name,\
    make_netid_changed_user_csv_file, make_regid_changed_user_csv_file,\
    make_key_changed_user_csv_files, get_restore_user_file_name,\
    make_restore_user_csv_file
from sis_provisioner.test import user_file_name_override


def get_users(size=1):
    users = []
    i = 0
    while i < size:
        users.append(UwBridgeUser(regid="11111111111111111111111111111111",
                                  netid="dummy",
                                  prev_netid="prev_dummy",
                                  last_visited_at=get_now(),
                                  first_name="Al",
                                  last_name="Dummy"))
        i += 1
    return users


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
                           BRIDGE_IMPORT_USER_FILE_SIZE=1):
            file_path = "/tmp"
            user_number = make_import_user_csv_files(None,
                                                     file_path,
                                                     False)
            self.assertEqual(user_number, 0)
            user_number = make_import_user_csv_files(get_users(3),
                                                     file_path,
                                                     False)
            self.assertEqual(user_number, 3)
            self.verify_file_content("/tmp/blah1.csv", False, False)
            self.verify_file_content("/tmp/blah2.csv", False, False)
            self.verify_file_content("/tmp/blah3.csv", False, False)

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

    def test_get_restore_user_file_name(self):
        file_path = "/tmp"
        self.assertEqual(get_restore_user_file_name(file_path),
                         "/tmp/users_restore.csv")

    def test_make_key_changed_user_csv_files_hrp(self):
        fp = "/tmp/users_xx_changed.csv"
        user_number = make_key_changed_user_csv_files(
            get_users(), fp, True, True)
        self.assertEqual(user_number, 1)
        self.verify_file_content(fp, True, True)

        user_number = make_key_changed_user_csv_files(
            get_users(), fp, False, True)
        self.assertEqual(user_number, 1)
        self.verify_file_content(fp, False,  True)

    def test_make_key_changed_user_csv_files(self):
        fp = "/tmp/users_xxx_changed.csv"
        user_number = make_key_changed_user_csv_files(
            get_users(), fp, False, False)
        self.assertEqual(user_number, 1)
        self.verify_file_content(fp, False, False)

    def test_make_delete_user_csv_file(self):
        user_number = make_delete_user_csv_file(get_users(), "/tmp")
        self.assertEqual(user_number, 1)
        fp = "/tmp/users_delete.csv"
        self.verify_file_content(fp, False, False)

    def test_make_netid_changed_user_csv_file(self):
        user_number = make_netid_changed_user_csv_file(
            get_users(), "/tmp", False)
        self.assertEqual(user_number, 1)
        fp = "/tmp/users_netid_changed.csv"
        self.verify_file_content(fp, True, False)

    def test_make_regid_changed_user_csv_file(self):
        user_number = make_regid_changed_user_csv_file(
            get_users(), "/tmp", False)
        self.assertEqual(user_number, 1)
        fp = "/tmp/users_regid_changed.csv"
        self.verify_file_content(fp, False, False)

    def test_make_restore_user_csv_file(self):
        user_number = make_restore_user_csv_file(
            get_users(), "/tmp", False)
        self.assertEqual(user_number, 1)
        fp = "/tmp/users_restore.csv"
        self.verify_file_content(fp, False, False)

    def verify_file_content(self, fp, is_uid_change, has_hrp_attrs):
        if has_hrp_attrs:
            if is_uid_change:
                expected = (
                    'prev uid,UNIQUE ID,NAME,EMAIL,regid' +
                    ',emp campus 1,emp coll 1,emp dept 1' +
                    ',emp campus 2,emp coll 2,emp dept 2' +
                    ',emp campus 3,emp coll 3,emp dept 3\n' +
                    'prev_dummy@uw.edu,dummy@uw.edu,Al Dummy,dummy@uw.edu,' +
                    '11111111111111111111111111111111,,,,,,,,,\n')
            else:
                expected = ('UNIQUE ID,NAME,EMAIL,regid' +
                            ',emp campus 1,emp coll 1,emp dept 1' +
                            ',emp campus 2,emp coll 2,emp dept 2' +
                            ',emp campus 3,emp coll 3,emp dept 3\n' +
                            'dummy@uw.edu,Al Dummy,dummy@uw.edu,' +
                            '11111111111111111111111111111111,,,,,,,,,\n')
        else:
            if is_uid_change:
                expected = (
                    'prev uid,UNIQUE ID,NAME,EMAIL,regid\n' +
                    'prev_dummy@uw.edu,dummy@uw.edu,Al Dummy,dummy@uw.edu,' +
                    '11111111111111111111111111111111\n')
            else:
                expected = ('UNIQUE ID,NAME,EMAIL,regid\n' +
                            'dummy@uw.edu,Al Dummy,dummy@uw.edu,' +
                            '11111111111111111111111111111111\n')
        try:
            fo = open(fp)
            result = fo.read()
            # print "%s====%s====%s" % (fp, has_hrp_attrs, result)
            self.assertEqual(result, expected)
        finally:
            os.remove(fp)
            self.assertFalse(os.path.exists(fp))
