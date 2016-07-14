import StringIO
import csv
import errno
import os
import stat
import re
import shutil
from datetime import datetime


FILEMODE = (stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP |
            stat.S_IROTH)
# ugo+x
DIRMODE = FILEMODE | (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def get_aline_csv(data):
    """
    Creates a line of csv data from the passed list of data.
    """
    s = StringIO.StringIO()

    csv.register_dialect("unix_newline", lineterminator="\n")
    writer = csv.writer(s, dialect="unix_newline")
    try:
        writer.writerow(data)
    except UnicodeEncodeError:
        print "Caught unicode error: %s" % data

    line = s.getvalue()
    s.close()
    return line


def get_filepath(path_prefix):
    """
    Create a fresh directory for the csv files
    """
    suffix = datetime.now().strftime('%Y%m%d-%H%M%S')
    print suffix
    filepath = os.path.join(path_prefix, suffix)
    os.makedirs(filepath)
    os.chmod(filepath, DIRMODE)
    return filepath


def open_file(full_path_file_name):
    fh = open(full_path_file_name, 'w')
    os.chmod(full_path_file_name, FILEMODE)
    return fh
