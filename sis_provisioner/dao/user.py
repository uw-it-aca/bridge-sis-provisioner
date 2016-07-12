"""
This module interacts with app's database
"""

import logging
import traceback
from django.core.exceptions import ObjectDoesNotExist
from restclients.exceptions import DataFailureException
from sis_provisioner.models.core import BridgeUser, get_now
from sis_provisioner.dao.pws import get_person


logger = logging.getLogger(__name__)


def get_user_from_db(uwnetid):
    try:
        return BridgeUser.objects.get(netid=uwnetid)
    except ObjectDoesNotExist:
        return None


def create_user(uwnetid):
    buser = get_bridgeuser_obj(get_person(uwnetid))
    updated_values = {'netid': uwnetid,
                      'last_visited_date': get_now(),
                      'display_name': buser.display_name,
                      'first_name': buser.first_name,
                      'last_name': buser.last_name,
                      'email': buser.email,
                      'home_department': buser.home_department,
                      'student_department1': buser.student_department1,
                      'student_department2': buser.student_department2,
                      'student_department3': buser.student_department3,
                      'is_alum': buser.is_alum,
                      'is_employee': buser.is_employee,
                      'is_faculty': buser.is_faculty,
                      'is_staff': buser.is_staff,
                      'is_student': buser.is_student,
                      }
    b_user, created = BridgeUser.objects.update_or_create(
        regid=buser.uwregid,
        defaults=updated_values)
    return b_user


def get_bridgeuser_obj(person):
    buser = BridgeUser()
    buser.netid = person.uwnetid
    buser.uwregid = person.uwregid
    buser.email = person.email1
    if not buser.email:
        buser.email = buser.netid + "@washington.edu"

    buser.display_name = person.display_name.title()
    buser.first_name = person.first_name.title()
    buser.last_name = person.surname.title()
    buser.home_department = person.home_department
    buser.student_department1 = person.student_department1
    buser.student_department2 = person.student_department2
    buser.student_department3 = person.student_department3
    buser.is_student = person.is_student
    buser.is_faculty = person.is_faculty
    buser.is_staff = person.is_staff
    buser.is_employee = person.is_employee
    buser.is_alum = person.is_alum
    return buser
