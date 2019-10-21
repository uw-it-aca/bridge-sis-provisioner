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


def get_person_changed_window():
    # number of minutes
    num = getattr(settings, 'BRIDGE_PERSON_CHANGE_WINDOW', None)
    return int(num) if num else 15


def get_worker_changed_window():
    # number of minutes
    num = getattr(settings, 'BRIDGE_WORKER_CHANGE_WINDOW', None)
    return int(num) if num else 15


def get_gws_cache_path():
    return getattr(settings, 'BRIDGE_GWS_CACHE', '')
