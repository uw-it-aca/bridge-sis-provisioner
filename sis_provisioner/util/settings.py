# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.conf import settings


def errors_to_abort_loader():
    return getattr(settings, 'ERRORS_TO_ABORT_LOADER', [])


def get_csv_file_path_prefix():
    return getattr(settings, 'BRIDGE_IMPORT_CSV_ROOT', '')


def get_csv_file_name_prefix():
    return getattr(settings, 'BRIDGE_IMPORT_USER_FILENAME', 'users')


def get_csv_file_size():
    max_size = getattr(settings, 'BRIDGE_IMPORT_USER_FILE_SIZE', None)
    return int(max_size) if max_size else 10000


def get_total_work_positions_to_load():
    num = getattr(settings, 'BRIDGE_USER_WORK_POSITIONS', None)
    return int(num) if num else 2


def get_author_group_name():
    return getattr(settings, 'BRIDGE_AUTHOR_GROUP_NAME', None)


def get_login_window():
    # number of days
    num = getattr(settings, 'BRIDGE_LOGIN_WINDOW', None)
    return int(num) if num else 0


def get_group_member_add_window():
    num = getattr(settings, 'BRIDGE_GMEMBER_ADD_WINDOW', None)
    return int(num) if num else 750  # 12.5 hr


def get_group_member_del_window():
    # number of days
    num = getattr(settings, 'BRIDGE_GMEMBER_DEL_WINDOW', None)
    return int(num) if num else 1470  # 24.5 hr


def get_person_changed_window():
    # number of minutes
    num = getattr(settings, 'BRIDGE_PERSON_CHANGE_WINDOW', None)
    return int(num) if num else 390  # 6 hr


def get_worker_changed_window():
    # number of minutes
    num = getattr(settings, 'BRIDGE_WORKER_CHANGE_WINDOW', None)
    return int(num) if num else 1470  # 24.5 hr


def check_all_accounts():
    return getattr(settings, 'CHECK_ALL_ACCOUNTS', False)
