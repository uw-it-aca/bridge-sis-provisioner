"""
This module interacts with app's database
"""

from datetime import timedelta
import logging
import re
import traceback
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from restclients.exceptions import DataFailureException
from restclients.hrpws.appointee import get_appointee_by_eid
from sis_provisioner.models import BridgeUser, get_now,\
    PRIORITY_NORMAL, PRIORITY_CHANGE_REGID, PRIORITY_CHANGE_NETID
from sis_provisioner.dao.hrp import get_appointee
from sis_provisioner.dao.pws import get_person
from sis_provisioner.util.log import log_exception


logger = logging.getLogger(__name__)


def create_user(uwnetid, include_hrp=False):
    """
    returns a BridgeUser object to add and a list of uwnetids to delete
    """
    try:
        person = get_person(uwnetid)
    except DataFailureException as ex:
        if ex.status == 404:
            logger.error("%s is not valid netid, skip!" % uwnetid)
        else:
            log_exception(logger,
                          "pws.person(%s) failed, skip" % uwnetid,
                          traceback.format_exc())
        return None, None

    if person.uwregid is None or len(person.uwregid) == 0:
        logger.error("%s has invalid uwregid, skip!" % uwnetid)
        return None, None
    return save_user(person, include_hrp)


def delete_user(uwnetid):
    """
    Return a list of uwnetids of the user record to be deleted from Bridge
    """
    return get_del_users(BridgeUser.objects.filter(netid=uwnetid))


def get_del_users(users):
    """
    Delete the users from DB is exists;
    Return a list of netids to be removed from Bridge, or None
    """
    if users is None or len(users) == 0:
        return None

    # having existing record, remove them
    users_deleted = []
    for user in users:
        users_deleted.append(user.netid)
    users.delete()
    return users_deleted


def get_all_users():
    return BridgeUser.objects.all()


def save_user(person, include_hrp):
    users_to_del = None
    user_in_db = None
    priority = PRIORITY_NORMAL
    bri_users = BridgeUser.objects.filter(Q(regid=person.uwregid) |
                                          Q(netid=person.uwnetid))
    if not bri_users or len(bri_users) == 0:
        pass
    else:
        if len(bri_users) == 1 and\
                bri_users[0].netid == person.uwnetid and\
                bri_users[0].regid == person.uwregid:
            user_in_db = bri_users[0]
        else:
            if changed_netid(bri_users, person):
                priority = PRIORITY_CHANGE_NETID
            else:
                priority = PRIORITY_CHANGE_REGID
            # having multi records or netid/regid changed
            users_to_del = get_del_users(bri_users)

    appointee = None
    if include_hrp and person.is_employee:
        appointee = get_appointee(person)

    if user_in_db is not None and\
            person_attr_not_changed(user_in_db, person) and\
            (appointee is None or emp_attr_not_changed(user_in_db, appointee)):
        user_in_db.save_verified()
        return None, users_to_del

    updated_values = {'netid': person.uwnetid,
                      'last_visited_date': get_now(),
                      'import_priority': priority,
                      'display_name': person.display_name,
                      'first_name': normalize_first_name(person.first_name),
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

    if appointee is not None:
        updated_values['hrp_home_dept_org_code'] =\
            appointee.home_dept_org_code
        updated_values['hrp_emp_status'] = appointee.status

    b_user, created = BridgeUser.objects.update_or_create(
        regid=person.uwregid,
        defaults=updated_values)
    return b_user, users_to_del


def emp_attr_not_changed(buser, appointee):
    return buser.hrp_home_dept_org_code == appointee.home_dept_org_code and\
        buser.hrp_emp_status == appointee.status


def person_attr_not_changed(buser, person):
    return buser.display_name == person.display_name and\
        buser.first_name == normalize_first_name(person.first_name) and\
        buser.last_name == person.surname and\
        buser.email == normalize_email(person.email1) and\
        buser.is_alum == person.is_alum and\
        buser.is_employee == person.is_employee and\
        buser.is_faculty == person.is_faculty and\
        buser.is_staff == person.is_staff and\
        buser.is_student == person.is_student and\
        buser.student_department1 == person.student_department1 and\
        buser.student_department2 == person.student_department2 and\
        buser.student_department3 == person.student_department3


def changed_netid(busers, person):
    for u in busers:
        if u.netid != person.uwnetid:
            return True
    return False


def normalize_email(email_str):
    if email_str is not None and len(email_str) > 0:
        return re.sub("\.$", "", email_str, flags=re.IGNORECASE)
    return email_str


def normalize_first_name(first_name):
    """
    Return a non NULL first name
    """
    if first_name is not None and len(first_name) > 0:
        return first_name
    return ""
