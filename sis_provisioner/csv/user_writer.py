import logging
import os
from django.conf import settings
from sis_provisioner.util.log import log_exception
from sis_provisioner.csv import get_aline_csv, open_file
from sis_provisioner.csv.user_formatter import get_headers, get_attr_list,\
    get_header_for_user_del


logger = logging.getLogger(__name__)


def _get_file_name_prefix():
    return getattr(settings, 'BRIDGE_IMPORT_USER_FILENAME', 'users')


def _get_file_size():
    max_size = getattr(settings, 'BRIDGE_IMPORT_USER_FILE_SIZE', '1000')
    return int(max_size) if max_size else 1000


def get_user_file_name(filepath, index):
    return os.path.join(filepath,
                        _get_file_name_prefix() + str(index) + '.csv')


def make_import_user_csv_files(users, filepath, include_hrp):
    """
    Writes all csv files. Returns number of records wrote out.
    """
    if not users or len(users) == 0:
        return 0

    total_users = len(users)
    f_index = 1
    user_number = 0
    f = open_file(get_user_file_name(filepath, f_index))
    f.write(get_aline_csv(get_headers(include_hrp)))

    for user in users:
        aline = get_aline_csv(get_attr_list(user, include_hrp))
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
            f = open_file(get_user_file_name(filepath, f_index))
            f.write(get_aline_csv(get_headers(include_hrp)))

    f.close()
    logger.info("Finish writing %d entries." % user_number)
    return user_number


def get_delete_user_file_name(filepath):
    return os.path.join(filepath,
                        _get_file_name_prefix() + '_delete.csv')


def make_delete_user_csv_file(netids, filepath):
    filename = get_delete_user_file_name(filepath)
    user_number = 0
    f = open_file(filename)
    f.write(get_aline_csv(get_header_for_user_del()))

    for netid in netids:
        aline = get_aline_csv([netids + "@washington.edu"])
        try:
            f.write(aline)
            user_number += 1
        except Exception:
            log_exception(
                logger,
                "Failed to write \"%s\" to the file %s, skip it." % (
                    (aline, filename)),
                traceback.format_exc())
            continue
    f.close()
    logger.info("Finish writing %d entries to %s." % (user_number, filename))
    return user_number


def get_regid_changed_file_name(filepath):
    return os.path.join(filepath,
                        _get_file_name_prefix() + '_regid_changed.csv')


def get_regid_changed_file_name(filepath):
    return os.path.join(filepath,
                        _get_file_name_prefix() + '_regid_changed.csv')


def make_import_netid_changed_user_csv_file(users, filepath, include_hrp):
    return make_key_changed_user_csv_files(
        users,
        get_netid_changed_file_name(filepath),
        include_hrp)


def make_import_regid_changed_user_csv_file(users, filepath, include_hrp):
    return make_key_changed_user_csv_files(
        users,
        get_regid_changed_file_name(filepath),
        include_hrp)


def make_key_changed_user_csv_files(users, filename, include_hrp):
    user_number = 0
    f = open_file(filename)
    f.write(get_aline_csv(get_headers(include_hrp)))

    for user in users:
        aline = get_aline_csv(get_attr_list(user, include_hrp))
        try:
            f.write(aline)
            user_number += 1
        except Exception:
            log_exception(
                logger,
                "Failed to write \"%s\" to the file %s, skip it." % (
                    (aline, filename)),
                traceback.format_exc())
            continue
    f.close()
    logger.info("Finish writing %d entries to %s." % (user_number, filename))
    return user_number
