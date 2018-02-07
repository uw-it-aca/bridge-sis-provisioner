"""
This module interacts with hrpws restclient for employee appointments
"""

import logging
import traceback
from restclients_core.exceptions import DataFailureException
from uw_hrp.appointee import get_appointee_by_regid
from sis_provisioner.models import EmployeeAppointment
from sis_provisioner.util.log import log_exception


logger = logging.getLogger(__name__)


def get_appointee(person):
    """
    Return the restclients...Appointee for the given Person object
    """
    try:
        return get_appointee_by_regid(person.uwregid)
    except Exception as ex:
        if ex.status == 404:
            logger.error("No appointee found for netid: %s!" % person.uwnetid)
        else:
            log_exception(logger,
                          "Failed to get appointee for %s" % person.uwnetid,
                          traceback.format_exc())
        return None


def get_appointments(person):
    """
    Return a list of EmployeeAppointment object.
    If no appointment, return an empty list.
    """
    emp_apps = []
    appointee = get_appointee(person)
    if appointee is not None:
        for app in sorted(appointee.appointments):
            emp_app = EmployeeAppointment(
                app_number=app.app_number,
                job_class_code=app.job_class_code,
                org_code=app.org_code)
            emp_apps.append(emp_app)
    return emp_apps
