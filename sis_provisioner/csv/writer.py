import logging
import traceback
from sis_provisioner.dao.uw_account import get_all_uw_accounts
from sis_provisioner.csv import get_filepath
from sis_provisioner.csv.user_writer import make_import_user_csv_files
from sis_provisioner.util.log import log_exception
from sis_provisioner.util.settings import get_csv_file_path_prefix

logger = logging.getLogger(__name__)


class CsvMaker:
    """
    For the given loader, create the corresponsing csv files.
    """
    def __init__(self,):
        """
        @param: loader an account_managers.loader subclass object
        """
        self.file_wrote = False
        self.filepath = get_filepath(path_prefix=get_csv_file_path_prefix())

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
