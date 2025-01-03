# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
This module encapsulates the interactions with the uw_pws,
"""

import logging
import traceback
from uw_pws import PWS
from sis_provisioner.dao import (
    DataFailureException, InvalidNetID, changed_since_str)
from sis_provisioner.util.log import log_exception, log_resp_time, Timer


logger = logging.getLogger(__name__)
pws = PWS()


def get_person(uwnetid):
    """
    Retrieve the Person object of the current uwnetid for the given netid
    Raise: DataFailureException if PWS returns a non-404 error
    """
    try:
        return pws.get_person_by_netid(uwnetid)
    except InvalidNetID:
        logger.error("Invalid uwnetid: {0}".format(uwnetid))
    except DataFailureException as ex:
        if ex.status == 404:
            logger.warning("{0} is not in PWS, skip!".format(uwnetid))
        else:
            log_exception(logger,
                          "get_person_by_netid({0}) ".format(uwnetid),
                          traceback.format_exc(chain=False))
    return None


def get_updated_persons(duration):
    """
    duration: time range in minutes
    Return a list of Person objects
    """
    timer = Timer()
    try:
        return pws.person_search(
            changed_since_date=changed_since_str(duration))
    except Exception:
        log_exception(logger, "get_updated_persons",
                      traceback.format_exc(chain=False))
        raise
    finally:
        log_resp_time(logger, "get_updated_persons", timer)
    return []


def is_prior_netid(uwnetid, person):
    """
    :param person: PWS Person object
    """
    return (uwnetid != person.uwnetid and
            len(person.prior_uwnetids) > 0 and
            uwnetid in person.prior_uwnetids)
