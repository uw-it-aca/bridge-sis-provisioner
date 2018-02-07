"""
This module interacts with the uw bridge user table in the app's database
"""

from datetime import timedelta
import json
import logging
import re
from string import capwords
import traceback
from django.db.models import Q
from restclients_core.exceptions import DataFailureException
from uw_hrp.appointee import get_appointee_by_eid
from sis_provisioner.models import UwBridgeUser, get_now, ACTION_UPDATE,\
    ACTION_NEW, ACTION_CHANGE_REGID, ACTION_RESTORE
from sis_provisioner.dao.hrp import get_appointments
from sis_provisioner.dao.pws import is_moved_netid, is_moved_regid
from sis_provisioner.util.log import log_exception


logger = logging.getLogger(__name__)


def get_all_users():
    return UwBridgeUser.objects.all()


def get_total_users():
    return len(get_all_users())


def get_users_from_db(bridgeid, uwnetid, uwregid):
    return UwBridgeUser.objects.filter(Q(regid=uwregid) |
                                       Q(netid=uwnetid) |
                                       Q(bridge_id=bridgeid))


def get_user_by_bridgeid(bridge_id):
    """
    @return a UwBridgeUser object
    @exception: UwBridgeUser.DoesNotExist
    """
    if bridge_id > 0:
        return UwBridgeUser.objects.get(bridge_id=bridge_id)
    return None


def get_user_by_netid(uwnetid):
    """
    @return a UwBridgeUser object
    @exception: UwBridgeUser.DoesNotExist
    """
    if uwnetid is not None:
        return UwBridgeUser.objects.get(netid=uwnetid)
    return None


def get_user_by_regid(uwregid):
    """
    returns a UwBridgeUser object
    @exception: UwBridgeUser.DoesNotExist
    """
    if uwregid is not None:
        return UwBridgeUser.objects.get(regid=uwregid)
    return None


def _filter_by_ids(uwnetid, uwregid):
    """
    returns a list of UwBridgeUser objects
    """
    return UwBridgeUser.objects.filter(Q(regid=uwregid) |
                                       Q(netid=uwnetid))


def save_user(person, include_hrp=True):
    """
    @return 1. the UwBridgeUser object of the account
               that needs to add/update/restore
            2. the UwBridgeUser object of the account
               that needs to be deleted
            None if n/a
            Documentation: https://wiki.cac.washington.edu/x/_zCIB
    """
    if person is None:
        return None, None

    action = ACTION_UPDATE
    changed_netids = None
    user_in_db = None
    user_deleted = None
    emp_apps_json_dump = None
    emp_apps_unchanged = True
    prev_netid = None

    uw_bri_users = _filter_by_ids(person.uwnetid, person.uwregid)
    if len(uw_bri_users) == 0:
        action = ACTION_NEW

    elif len(uw_bri_users) == 1:
        # one existing account
        old_user = _get_netid_changed_user(uw_bri_users, person)
        if old_user is not None:
            prev_netid = old_user.netid

        if uw_bri_users[0].disabled:
            action = ACTION_RESTORE

        if _changed_regid(uw_bri_users, person):
            uw_bri_users.delete()
            if action != ACTION_RESTORE:
                action = ACTION_CHANGE_REGID
        else:
            user_in_db = uw_bri_users[0]
    else:
        # two existing accounts
        logger.info("(%s, %s) has two accounts: %s, %s" %
                    (person.uwnetid, person.uwregid,
                     uw_bri_users[0], uw_bri_users[1]))
        old_user = _get_netid_changed_user(uw_bri_users, person)

        if _are_all_disabled(uw_bri_users):
            action = ACTION_RESTORE
        elif _are_all_active(uw_bri_users):
            # delete the one with the old netid
            if old_user is not None:
                user_deleted = old_user
                prev_netid = old_user.netid
        else:
            # one is active and one is disabled
            if not old_user.disabled:
                prev_netid = old_user.netid
        uw_bri_users.delete()

    if include_hrp:
        emp_apps_json_dump = _appointments_json_dump(person)
        if user_in_db is not None:
            emp_apps_unchanged = _emp_attr_unchanged(
                user_in_db.emp_appointments_data, emp_apps_json_dump)

    if user_in_db is not None and\
            _person_attr_unchanged(user_in_db, person) and emp_apps_unchanged:
        if action == ACTION_RESTORE:
            user_in_db.save_verified(action=action)
        else:
            user_in_db.save_verified()
        return user_in_db, user_deleted

    updated_values = _get_user_updated_values(person, prev_netid, action)

    if user_in_db is None or not emp_apps_unchanged:
        updated_values['emp_appointments_data'] = emp_apps_json_dump

    b_user, created = UwBridgeUser.objects.update_or_create(
        regid=person.uwregid, defaults=updated_values)
    return b_user, user_deleted


def _appointments_json_dump(person):
    """
    @param person valid PWS Person object
    """
    apps_json = []
    if person.is_employee:
        appointments = get_appointments(person)
        if len(appointments) > 0:
            for app in appointments:
                apps_json.append(app.to_json())
    return json.dumps(apps_json, separators=(',', ':'), sort_keys=True)


def _emp_attr_unchanged(old_appointments_json_dump,
                        upt_appointments_json_dump):
    """
    return True if employee appointment data not changed
    """
    return ((old_appointments_json_dump is None and
             upt_appointments_json_dump is None) or
            old_appointments_json_dump == upt_appointments_json_dump)


def _person_attr_unchanged(buser, person):
    """
    @param person valid PWS Person object
    @param: busers a list of UwBrifgeUser
    return True if attibutes have not changed
    """
    return buser.display_name == person.display_name and\
        buser.first_name == normalize_name(person.first_name) and\
        buser.last_name == normalize_name(person.surname) and\
        buser.email == normalize_email(person.email1) and\
        buser.is_employee == person.is_employee
    #    buser.is_alum == person.is_alum and\
    #    buser.is_faculty == person.is_faculty and\
    #    buser.is_staff == person.is_staff and\
    #    buser.is_student == person.is_student


def _are_all_active(busers):
    """
    @param: busers a list of UwBrifgeUser
    return True if all user records are not disabled
    """
    for u in busers:
        if u.disabled:
            return False
    return True


def _are_all_disabled(busers):
    """
    @param: busers a list of UwBrifgeUser
    return True if all user records are not disabled
    """
    for u in busers:
        if not u.disabled:
            return False
    return True


def _get_netid_changed_user(busers, person):
    """
    @param: busers a list of UwBrifgeUser
    @param: person a pws Person
    return the user with the old netid
    """
    for u in busers:
        if u.netid != person.uwnetid and\
           is_moved_netid(u.netid):
            logger.info("Existing user %s has changed netid from %s to %s" %
                        (u, u.netid, person.uwnetid))
            return u
    return None


def _changed_regid(busers, person):
    """
    @param: busers a list of UwBrifgeUser
    @param: person a valid pws Person object
    """
    for u in busers:
        if u.regid != person.uwregid and\
           is_moved_regid(u.regid):
            logger.info("Existing user %s has changed regid from %s to %s" %
                        (u, u.regid, person.uwregid))
            return True
    return False


def _get_user_updated_values(person, prev_netid, action):
    """
    @param person valid PWS Person object
    @param prev_netid can be None
    @param action one of the ACTION_CHOICES in models.py
    """
    return {'netid': person.uwnetid,
            'prev_netid': prev_netid,
            'last_visited_at': get_now(),
            'disabled': False,
            'terminate_at': None,
            'action_priority': action,
            'display_name': person.display_name,
            'first_name': normalize_name(person.first_name),
            'last_name': normalize_name(person.surname),
            'email': normalize_email(person.email1),
            'is_employee': person.is_employee,
            # 'is_alum': person.is_alum,
            # 'is_faculty': person.is_faculty,
            # 'is_staff': person.is_staff,
            # 'is_student': person.is_student
            }


def normalize_email(email_str):
    if email_str is not None and len(email_str) > 0:
        email_s1 = re.sub(" ", "", email_str)
        return re.sub("\.$", "", email_s1, flags=re.IGNORECASE)
    return email_str


def normalize_name(name):
    """
    Return a title faced name if the name is not empty
    """
    if name is not None and len(name) > 0:
        return capwords(name)
    return ""
