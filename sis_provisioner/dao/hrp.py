"""
This module interacts with app's database
"""

import logging
import traceback
from restclients.exceptions import DataFailureException
from restclients.hrpws.appointee import get_appointee_by_eid
from sis_provisioner.util.log import log_exception


logger = logging.getLogger(__name__)


def get_appointee(person):
    """
    Return the restclients...Appointee for the given Person object
    """
    try:
        return get_appointee_by_eid(person.employee_id)
    except Exception:
        log_exception(logger,
                      "Failed to get appointee for %s" % person.uwnetid,
                      traceback.format_exc())
        return None
