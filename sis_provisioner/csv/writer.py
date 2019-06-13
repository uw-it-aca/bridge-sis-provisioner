import logging
import traceback
from django.conf import settings
from sis_provisioner.dao.uw_account import get_all_uw_accounts
from sis_provisioner.csv import get_filepath
from sis_provisioner.csv.user_writer import make_import_user_csv_files
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
        raise


class CsvMaker:
    """
    For the given loader, create the corresponsing csv files.
    """
    def __init__(self,):
        """
        @param: loader an account_managers.loader subclass object
        """
        self.file_wrote = False
        self.filepath = get_file_path()

    def fetch_users(self):
        return get_all_uw_accounts()

    def load_files(self):
        try:
            number_users_wrote = make_import_user_csv_files(
                self.fetch_users(), self.filepath)
            logger.info("Total {0:d} users wrote into {1}\n".format(
                number_users_wrote, self.filepath))
            return number_users_wrote
        except Exception:
            log_exception(
                logger,
                "Failed to make user csv file in {0}".format(self.filepath),
                traceback.format_exc())
