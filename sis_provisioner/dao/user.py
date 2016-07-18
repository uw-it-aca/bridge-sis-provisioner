"""
This module interacts with app's database
"""

import logging
import re
import traceback
from django.core.exceptions import ObjectDoesNotExist
from restclients.exceptions import DataFailureException
from restclients.hrpws.appointee import get_appointee_by_eid
from sis_provisioner.models.core import BridgeUser, get_now
from sis_provisioner.dao.hrp import get_appointee
from sis_provisioner.dao.pws import get_person


logger = logging.getLogger(__name__)


def get_user_from_db(uwnetid):
    try:
        return BridgeUser.objects.get(netid=uwnetid)
    except ObjectDoesNotExist:
        return None


def get_first_name(person):
    """
    Return a non NULL first name
    """
    if not person.first_name:
        return ""
    else:
        return person.first_name


def normalize_email(email_str):
    if email_str:
        return re.sub(".$", "", email_str, flags=re.IGNORECASE)
    return email_str


def create_user(uwnetid):
    person = get_person(uwnetid)
    first_name = ""
    if person.first_name:
        first_name = person.first_name

    updated_values = {'netid': uwnetid,
                      'last_visited_date': get_now(),
                      'display_name': person.display_name,
                      'first_name': get_first_name(person),
                      'last_name': person.surname,
                      'email': normalize_email(person.email1),
                      'is_alum': person.is_alum,
                      'is_employee': person.is_employee,
                      'is_faculty': person.is_faculty,
                      'is_staff': person.is_staff,
                      'is_student': person.is_student,
                      'student_department1': person.student_department1,
                      'student_department2': person.student_department2,
                      'student_department3': person.student_department3,
                      }
    appointee = None
    if person.is_employee:
        appointee = get_appointee(person)
        if appointee is not None:
            updated_values['hrp_home_dept_org_code'] =\
                appointee.home_dept_org_code
            updated_values['hrp_home_dept_org_name'] =\
                appointee.home_dept_org_name
            updated_values['hrp_emp_status'] = appointee.status

    b_user, created = BridgeUser.objects.update_or_create(
        regid=person.uwregid,
        defaults=updated_values)
    return b_user
