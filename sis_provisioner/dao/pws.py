"""
This module encapsulates the interactions with the uw_pws,
"""

import logging
import traceback
from uw_pws import PWS
from sis_provisioner.dao import DataFailureException, InvalidNetID
from sis_provisioner.util.log import log_exception


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


def is_active_worker(person):
    """
    is_employee: faculty, staff, student employee with a grace period.
    is_emp_state_current: is_employee plus affiliates and retiree
    but no grace period. It reflects within 24 hours of a status change.
    """
    return person.is_employee or person.is_emp_state_current()


def is_prior_netid(uwnetid, person):
    """
    :param person: PWS Person object
    """
    return (uwnetid != person.uwnetid and
            len(person.prior_uwnetids) > 0 and
            uwnetid in person.prior_uwnetids)
