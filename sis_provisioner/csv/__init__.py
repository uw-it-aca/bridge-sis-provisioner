# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import io
import csv
import os
import logging
import traceback
from datetime import datetime
from django.core.files.storage import default_storage
from sis_provisioner.util.log import log_exception

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


def get_filepath(path_prefix=''):
    """
    Create a fresh directory for the csv files
    """
    path = datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    if len(path_prefix):
        path = os.path.join(path_prefix, path)
    return path


def open_file(full_path_file_name):
    return default_storage.open(full_path_file_name, mode='w')
