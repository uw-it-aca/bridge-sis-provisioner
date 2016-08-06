import os
import re
from django.conf import settings
from django.test import TransactionTestCase
from django.test.utils import override_settings
from sis_provisioner.models import BridgeUser, get_now
from sis_provisioner.test import FGWS, FPWS, FHRP
from sis_provisioner.user_loader import UserLoader
from sis_provisioner.user_checker import PurgeUserLoader
from sis_provisioner.csv_writer import _get_file_path_prefix,\
    get_file_path, CsvFileMaker


class TestCsvWriter(TransactionTestCase):

    def test_get_file_path_prefix(self):
        with self.settings(BRIDGE_IMPORT_CSV_ROOT="/tmp/fl_test"):
            self.assertEqual(_get_file_path_prefix(), "/tmp/fl_test")

    def test_get_file_path(self):
        with self.settings(BRIDGE_IMPORT_CSV_ROOT="/tmp/fl_test"):
            fp = get_file_path()
            self.assertIsNotNone(fp)
            self.assertTrue(re.match("/tmp/fl_test/[2-9]\d{7}-\d{6}", fp))
            self.assertTrue(os.path.exists(fp))
            os.rmdir(fp)

    def test_csv_file_maker_with_user_loader(self):
        with self.settings(RESTCLIENTS_GWS_DAO_CLASS=FGWS,
                           RESTCLIENTS_PWS_DAO_CLASS=FPWS,
                           BRIDGE_IMPORT_CSV_ROOT="/tmp",
                           BRIDGE_IMPORT_USER_FILENAME='busrs',
                           BRIDGE_IMPORT_USER_FILE_SIZE=3):
            user_loader = UserLoader(include_hrp=False)
            user_loader.init_set()
            self.assertEqual(user_loader.get_add_count(), 0)
            self.assertEqual(user_loader.get_delete_count(), 0)
            self.assertEqual(user_loader.get_netid_changed_count(), 0)
            self.assertEqual(user_loader.get_regid_changed_count(), 0)

            maker = CsvFileMaker(user_loader)
            fp = maker.get_file_path()
            self.assertTrue(re.match("/tmp/[2-9]\d{7}-\d{6}", fp))

            number_users_wrote = maker.make_add_user_files()
            self.assertEqual(number_users_wrote, 8)
            self.assertTrue(os.path.exists(fp + "/busrs1.csv"))
            self.assertTrue(os.path.exists(fp + "/busrs2.csv"))
            self.assertTrue(os.path.exists(fp + "/busrs3.csv"))
            os.remove(fp + "/busrs1.csv")
            os.remove(fp + "/busrs2.csv")
            os.remove(fp + "/busrs3.csv")
            os.removedirs(fp)

            number_users_wrote = maker.make_netid_change_user_file()
            self.assertEqual(number_users_wrote, 0)

            number_users_wrote = maker.make_regid_change_user_file()
            self.assertEqual(number_users_wrote, 0)

            number_users_wrote = maker.make_delete_user_file()
            self.assertEqual(number_users_wrote, 0)

    def test_csv_file_maker_with_user_checker(self):
        with self.settings(RESTCLIENTS_GWS_DAO_CLASS=FGWS,
                           RESTCLIENTS_PWS_DAO_CLASS=FPWS,
                           BRIDGE_IMPORT_CSV_ROOT="/tmp/fl_test",
                           BRIDGE_IMPORT_USER_FILENAME='busrs',
                           BRIDGE_IMPORT_USER_FILE_SIZE=3):
            # pre-load users into database
            loader = UserLoader(include_hrp=False)
            loader.fetch_all()
            # check existing users
            duser_loader = PurgeUserLoader()
            duser_loader.init_set()
            self.assertEqual(duser_loader.get_total_count(), 0)
            self.assertEqual(duser_loader.get_delete_count(), 0)
            self.assertEqual(duser_loader.get_users_left_uw_count(), 0)

            maker = CsvFileMaker(duser_loader)
            fp = maker.get_file_path()
            self.assertTrue(re.match("/tmp/fl_test/[2-9]\d{7}-\d{6}", fp))
            number_users_wrote = maker.make_delete_user_file()
            self.assertEqual(number_users_wrote, 1)
            self.assertTrue(os.path.exists(fp + "/busrs_delete.csv"))
            os.remove(fp + "/busrs_delete.csv")
            os.removedirs(fp)
