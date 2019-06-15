import logging
import os
from django.conf import settings
from sis_provisioner.dao.pws import get_person
from sis_provisioner.dao.hrp import get_worker
from sis_provisioner.util.log import log_exception
from sis_provisioner.csv import get_aline_csv, open_file
from sis_provisioner.csv.user_formatter import BASIC_HEADERS, get_attr_list


logger = logging.getLogger(__name__)


def _get_file_name_prefix():
    return getattr(settings, 'BRIDGE_IMPORT_USER_FILENAME', 'users')


def _get_file_size():
    max_size = getattr(settings, 'BRIDGE_IMPORT_USER_FILE_SIZE', '1000')
    return int(max_size) if max_size else 1000


def get_user_file_name(filepath, index):
    return os.path.join(filepath,
                        _get_file_name_prefix() + str(index) + '.csv')


def make_import_user_csv_files(uw_accounts,
                               filepath):
    """
    :param uw_accounts: a list of UwAccount objects
    Writes all csv files. Returns number of records wrote out.
    """
    if not uw_accounts or len(uw_accounts) == 0:
        return 0

    total_users = len(uw_accounts)
    f_index = 1
    user_number = 0
    csv_headers = get_aline_csv(BASIC_HEADERS)
    f = open_file(get_user_file_name(filepath, f_index))
    f.write(csv_headers)

    for uw_account in uw_accounts:
        if uw_account.disabled or uw_account.has_terminate_date():
            continue
        person = get_person(uw_account.netid)
        if person.home_department is None:
            continue
        if person.uwnetid != uw_account.netid:
            logger.error("OLD netid, Skip {0}".format(uw_account))
            continue
        aline = get_aline_csv(get_attr_list(person, get_worker(person)))
        try:
            f.write(aline)
        except Exception:
            log_exception(
                logger,
                "{0:d}th file: ({1}), Skip!".format(f_index, aline),
                traceback.format_exc())
            continue

        user_number += 1
        if (user_number < total_users and
                (user_number % _get_file_size()) == 0):
            f.close()
            logger.info("Finish writing {0:d} entries.".format(user_number))
            f_index += 1
            f = open_file(get_user_file_name(filepath, f_index))
            f.write(csv_headers)

    f.close()
    logger.info("Finish writing {0:d} entries.".format(user_number))
    return user_number
