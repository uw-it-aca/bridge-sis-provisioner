import os
import re
import shutil
from django.conf import settings
from django.test import TransactionTestCase
from django.test.utils import override_settings
from sis_provisioner.models import UwBridgeUser, get_now, ACTION_UPDATE,\
    ACTION_NEW, ACTION_CHANGE_REGID, ACTION_RESTORE
from sis_provisioner.account_managers.gws_bridge import GwsBridgeLoader
from sis_provisioner.account_managers.reload_bridge import Reloader
from sis_provisioner.account_managers.csv_worker import CsvWorker
from sis_provisioner.csv_writer import _get_file_path_prefix,\
    get_file_path, CsvFileMaker
from sis_provisioner.test import FGWS, FPWS


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

    def test_get_file_path_exce(self):
        with self.settings(BRIDGE_IMPORT_CSV_ROOT="/usr"):
            self.assertRaises(OSError, get_file_path)

    def test_load_user_csv_file(self):
        with self.settings(RESTCLIENTS_GWS_DAO_CLASS=FGWS,
                           RESTCLIENTS_PWS_DAO_CLASS=FPWS,
                           BRIDGE_IMPORT_CSV_ROOT="/tmp/fl_test",
                           BRIDGE_IMPORT_USER_FILENAME='busrs',
                           BRIDGE_IMPORT_USER_FILE_SIZE=3):
            user_loader = GwsBridgeLoader(CsvWorker(),
                                          include_hrp=False)
            maker = CsvFileMaker(user_loader)
            fp = maker.get_file_path()
            self.assertTrue(re.match("/tmp/fl_test/[2-9]\d{7}-\d{6}", fp))
            self.assertEqual(user_loader.get_loaded_count(), 8)
            self.assertEqual(user_loader.get_deleted_count(), 0)
            self.assertEqual(user_loader.get_netid_changed_count(), 0)
            self.assertEqual(user_loader.get_regid_changed_count(), 0)

            number_users_wrote = maker.make_load_user_files()
            self.assertTrue(maker.is_file_wrote())
            self.assertEqual(number_users_wrote, 8)
            self.assertTrue(os.path.exists(fp + "/busrs1.csv"))
            self.assertTrue(os.path.exists(fp + "/busrs2.csv"))
            self.assertTrue(os.path.exists(fp + "/busrs3.csv"))
            os.remove(fp + "/busrs1.csv")
            os.remove(fp + "/busrs2.csv")
            os.remove(fp + "/busrs3.csv")
            os.rmdir(fp)

    def test_netid_change_user_csv_file(self):
        with self.settings(BRIDGE_IMPORT_CSV_ROOT="/tmp/fl_test",
                           BRIDGE_IMPORT_USER_FILENAME='busrs'):
            user = UwBridgeUser(netid='changed',
                                bridge_id=195,
                                prev_netid='javerage',
                                regid="9136CCB8F66711D5BE060004AC494FFE",
                                action_priority=ACTION_UPDATE,
                                last_visited_at=get_now(),
                                first_name="Changed",
                                last_name="Netid")
            user.save()
            maker = CsvFileMaker(Reloader(CsvWorker(),
                                          include_hrp=False))
            fp = maker.get_file_path()
            number_users_wrote = maker.make_netid_change_user_file()
            self.assertEqual(number_users_wrote, 1)
            self.assertTrue(maker.is_file_wrote())
            os.remove(fp + "/busrs_netid_changed.csv")
            os.rmdir(fp)

    def test_restore_user_csv_file(self):
        with self.settings(BRIDGE_IMPORT_CSV_ROOT="/tmp/fl_test",
                           BRIDGE_IMPORT_USER_FILENAME='busrs'):
            user = UwBridgeUser(netid='javerage',
                                bridge_id=195,
                                regid="0136CCB8F66711D5BE060004AC494FFE",
                                last_visited_at=get_now(),
                                last_name="Restore")
            user.action_priority = ACTION_RESTORE
            user.save()
            maker = CsvFileMaker(Reloader(CsvWorker(),
                                          include_hrp=False))
            fp = maker.get_file_path()
            number_users_wrote = maker.make_restore_user_file()
            self.assertEqual(number_users_wrote, 1)
            self.assertTrue(maker.is_file_wrote())
            os.remove(fp + "/busrs_restore.csv")
            os.rmdir(fp)

    def test_delete_user_csv_file(self):
        with self.settings(BRIDGE_IMPORT_CSV_ROOT="/tmp/fl_test",
                           BRIDGE_IMPORT_USER_FILENAME='busrs'):
            user = UwBridgeUser(netid='javerage',
                                regid="0136CCB8F66711D5BE060004AC494FFE",
                                bridge_id=195,
                                last_visited_at=get_now(),
                                terminate_at=get_now(),
                                last_name="Delete")
            user.save()
            user_loader = Reloader(CsvWorker())
            maker = CsvFileMaker(user_loader)
            fp = maker.get_file_path()
            number_users_wrote = maker.make_delete_user_file()
            self.assertEqual(number_users_wrote, 1)
            self.assertTrue(maker.is_file_wrote())
            os.remove(fp + "/busrs_delete.csv")
            os.rmdir(fp)

    def test_regid_change_csv_file(self):
        with self.settings(BRIDGE_IMPORT_CSV_ROOT="/tmp/fl_test",
                           BRIDGE_IMPORT_USER_FILENAME='busrs'):
            user = UwBridgeUser(netid='javerage',
                                regid="0136CCB8F66711D5BE060004AC494FFE",
                                action_priority=ACTION_CHANGE_REGID,
                                last_visited_at=get_now(),
                                email='javerage@uw.edu',
                                first_name="James",
                                last_name="Student")
            user.save()
            user_loader = Reloader(CsvWorker(),
                                   include_hrp=False)
            maker = CsvFileMaker(user_loader)
            fp = maker.get_file_path()
            number_users_wrote = maker.make_regid_change_user_file()
            self.assertEqual(number_users_wrote, 1)
            self.assertTrue(maker.is_file_wrote())
            os.remove(fp + "/busrs_regid_changed.csv")
            os.rmdir(fp)
