from datetime import datetime
import logging
import os
from restclients_core.exceptions import (
    DataFailureException, InvalidNetID, InvalidRegID)


logger = logging.getLogger(__name__)


def read_gws_cache_file(path):
    user_set = set()
    if os.path.isfile(path):
        with open(path, 'r', encoding='utf8') as data_source:
            for line in data_source:
                try:
                    user_set.add(line.rstrip())
                except Exception as ex:
                    logger.error("read_file({}) line {} ==>{}".format(
                        path, line, str(ex)))
    return user_set


def rename_file(path):
    rname = "{}.{}".format(path, datetime.now().strftime("%Y%m%d.%H%M"))
    try:
        os.rename(path, rname)
    except Exception as ex:
        logger.error("rename_file({}, {}) ==>{}".format(path, rname, str(ex)))


def write_gws_cache_file(path, user_set):
    if os.path.isfile(path):
        rename_file(path)

    f = open(path, "w")
    for netid in sorted(list(user_set)):
        try:
            f.write("{}\n".format(netid))
        except Exception as ex:
            logger.error("{} write_gws_cache_file({}) Skip {}".format(
                str(ex), path, netid))
            continue
    f.close()
