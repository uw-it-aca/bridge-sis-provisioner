import logging
import os
from django.conf import settings
from sis_provisioner.util.log import log_exception
from sis_provisioner.csv import get_aline_csv, get_filepath, open_file
from sis_provisioner.csv.user_formatter import get_headers, get_attr_list


logger = logging.getLogger(__name__)


def _get_file_path_prefix():
    return getattr(settings, 'BRIDGE_IMPORT_CSV_ROOT', '')


def _get_file_size():
    max_size = getattr(settings, 'BRIDGE_IMPORT_USER_FILE_SIZE', '1000')
    return int(max_size) if max_size else 1000


def get_file_name(filepath, index):
    filename = getattr(settings, 'BRIDGE_IMPORT_USER_FILENAME', 'users')
    return os.path.join(filepath,
                        filename + str(index) + '.csv')


def write_files(users):
    """
    Writes all csv files. Returns a path to the csv files, or None
    if no data was written.
    """
    if not users or len(users) == 0:
        return None

    total_users = len(users)
    path_prefix = _get_file_path_prefix()
    try:
        filepath = get_filepath(path_prefix)
    except Exception:
        log_exception(logger,
                      "Cannot create CSV dir %s" % path_prefix,
                      traceback.format_exc())
        return

    f_index = 1
    user_number = 0
    f = open_file(get_file_name(filepath, f_index))
    f.write(get_aline_csv(get_headers()))

    for user in users:
        aline = get_aline_csv(get_attr_list(user))
        try:
            f.write(aline)
        except Exception:
            log_exception(
                logger,
                ("Failed to write \"%s\" to the %dth file, skip it." % (
                        aline, f_index)),
                traceback.format_exc())
            continue

        user_number += 1
        if user_number < total_users and\
                (user_number % _get_file_size()) == 0:
            f.close()
            logger.info("Finish writing %d entries." % user_number)
            f_index += 1
            f = open_file(get_file_name(filepath, f_index))
            f.write(get_aline_csv(get_headers()))

    f.close()

    logger.info("Total %d users wrote into %s.\n" % (
            user_number, filepath))
    return filepath
