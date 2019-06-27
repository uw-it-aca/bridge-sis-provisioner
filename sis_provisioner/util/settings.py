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
