import io
import csv
import errno
import os
import stat
import re
import shutil
import logging
import traceback
from datetime import datetime
from sis_provisioner.util.log import log_exception


FILEMODE = (stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP |
            stat.S_IROTH)
# ugo+x
DIRMODE = FILEMODE | (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
logger = logging.getLogger(__name__)


def get_aline_csv(data):
    """
    Create a line of csv data from the passed list of data.
    """
    s = io.StringIO()

    csv.register_dialect("unix_newline", lineterminator="\n")
    writer = csv.writer(s, dialect="unix_newline")
    try:
        writer.writerow(data)
    except UnicodeEncodeError:
        log_exception(logger,
                      "get_aline_csv [{0}]".format(','.join(data)),
                      traceback.format_exc())

    line = s.getvalue()
    s.close()
    return line


def get_filepath(path_prefix):
    """
    Create a fresh directory for the csv files
    """
    suffix = datetime.now().strftime('%Y%m%d-%H%M%S')
    filepath = os.path.join(path_prefix, suffix)
    os.makedirs(filepath, DIRMODE)
    # makes all intermediate-level directories needed
    return filepath


def open_file(full_path_file_name):
    fh = open(full_path_file_name, 'w')
    os.chmod(full_path_file_name, FILEMODE)
    return fh
