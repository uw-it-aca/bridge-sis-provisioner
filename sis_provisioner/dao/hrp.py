# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
This module interacts with hrpws restclient for employee appointments
"""

import logging
import traceback
from sis_provisioner.dao import (
    DataFailureException, InvalidRegID, changed_since_str)
from uw_hrp import HRP
from sis_provisioner.util.log import log_exception, log_resp_time, Timer


logger = logging.getLogger(__name__)
hrp = HRP()


def get_worker(person):
    """
    Return the Appointee for the given Person object
    """
    netid = person.uwnetid
    try:
        return hrp.get_person_by_regid(person.uwregid)
    except InvalidRegID:
        logger.error(f"{netid} has invalid uwregid")
    except DataFailureException as ex:
        if ex.status != 404:
            log_exception(
                logger,
                f"Failed to get worker({netid}): {ex}",
                traceback.format_exc(chain=False))
    return None


def get_worker_updates(duration):
    """
    duration: time range in minutes
    Return a list of WorkerRef objects
    """
    timer = Timer()
    try:
        return hrp.person_search(
            changed_since_date=changed_since_str(duration, iso=True))
    except Exception as ex:
        log_exception(
            logger, f"get_worker_updates: {ex}",
            traceback.format_exc(chain=False))
        raise
    finally:
        log_resp_time(logger, "get_worker_updates", timer)
    return []
