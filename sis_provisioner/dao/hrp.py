# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
This module interacts with hrpws restclient for employee appointments
"""

import logging
import traceback
from sis_provisioner.dao import (
    DataFailureException, InvalidRegID, changed_since_str)
from uw_hrp.worker import get_worker_by_regid, worker_search
from sis_provisioner.util.log import log_exception, log_resp_time, Timer


logger = logging.getLogger(__name__)


def get_worker(person):
    """
    Return the Appointee for the given Person object
    """
    try:
        if person.is_emp_state_current():
            return get_worker_by_regid(person.uwregid)
    except InvalidRegID:
        logger.error("'{0}' has invalid uwregid".format(person.uwnetid))
    except DataFailureException as ex:
        log_exception(
            logger,
            "Failed to get worker for '{0}'".format(person.uwnetid),
            traceback.format_exc(chain=False))
    return None


def get_worker_updates(duration):
    """
    duration: time range in minutes
    Return a list of WorkerRef objects
    """
    timer = Timer()
    try:
        return worker_search(changed_since=changed_since_str(duration))
    except Exception:
        log_exception(logger, "get_worker_updates",
                      traceback.format_exc(chain=False))
        raise
    finally:
        log_resp_time(logger, "get_worker_updates", timer)
    return []
