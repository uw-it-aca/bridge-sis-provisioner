import logging
import traceback
from django.conf import settings
from restclients.exceptions import DataFailureException
from sis_provisioner.csv import get_filepath
from sis_provisioner.csv.user_writer import make_import_user_csv_files,\
    make_import_regid_changed_user_csv_file,\
    make_import_netid_changed_user_csv_file, make_delete_user_csv_file
from sis_provisioner.util.log import log_exception


logger = logging.getLogger(__name__)


def _get_file_path_prefix():
    return getattr(settings, 'BRIDGE_IMPORT_CSV_ROOT', '')


def get_file_path():
    path_prefix = _get_file_path_prefix()
    try:
        return get_filepath(path_prefix)
    except Exception:
        log_exception(logger,
                      "Cannot create CSV dir %s" % path_prefix,
                      traceback.format_exc())
        return None


class CsvFileMaker:
    """
    For the given loader, create the corresponsing csv files.
    """
    def __init__(self, loader, include_hrp=False):
        self.file_wrote = False
        self.include_hrp_data = include_hrp
        self.filepath = get_file_path()
        self.loader = loader
        self.loader.fetch_all()

    def get_file_path(self):
        return self.filepath

    def is_file_wrote(self):
        return self.file_wrote

    def _set_file_wrote(self):
        if not self.file_wrote:
            self.file_wrote = True

    def make_add_user_files(self):
        if self.loader.get_add_count() == 0:
            return 0
        try:
            number_users_wrote = make_import_user_csv_files(
                self.loader.get_users_to_add(),
                self.filepath,
                self.include_hrp_data)
            self._set_file_wrote()
            logger.info("Total %d users (to add/upd) wrote into %s.\n" % (
                    number_users_wrote, self.filepath))
            return number_users_wrote
        except Exception:
            log_exception(logger,
                          "Failed to make user csv file in %s" %
                          self.filepath,
                          traceback.format_exc())
            raise

    def make_netid_change_user_file(self):
        if self.loader.get_netid_changed_count() == 0:
            return 0
        try:
            number_users_wrote = make_import_netid_changed_user_csv_file(
                self.loader.get_users_netid_changed(),
                self.filepath,
                self.include_hrp_data)
            self._set_file_wrote()
            logger.info("Total %d users (netid changed) wrote into %s.\n" % (
                    number_users_wrote, self.filepath))
            return number_users_wrote
        except Exception:
            log_exception(logger,
                          "Failed to make netid changed user file in %s" %
                          self.filepath,
                          traceback.format_exc())
            raise

    def make_regid_change_user_file(self):
        if self.loader.get_regid_changed_count() == 0:
            return 0
        try:
            number_users_wrote = make_import_regid_changed_user_csv_file(
                self.loader.get_users_regid_changed(),
                self.filepath,
                self.include_hrp_data)
            self._set_file_wrote()
            logger.info("Total %d users (regid changed) wrote into %s.\n" % (
                    number_users_wrote, self.filepath))
            return number_users_wrote
        except Exception:
            log_exception(logger,
                          "Failed to make regid changed user file in %s" %
                          self.filepath,
                          traceback.format_exc())
            raise

    def make_delete_user_file(self):
        if self.loader.get_delete_count() == 0:
            return 0
        try:
            number_users_wrote = make_delete_user_csv_file(
                self.loader.get_users_to_delete(),
                self.filepath)
            self._set_file_wrote()
            logger.info("Total %d users (to delete) wrote into %s.\n" % (
                    number_users_wrote, self.filepath))
            return number_users_wrote
        except Exception:
            log_exception(logger,
                          "Failed to make delete user file in %s" %
                          self.filepath,
                          traceback.format_exc())
            raise
