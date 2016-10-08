import logging
import traceback
from restclients.exceptions import DataFailureException
from sis_provisioner.dao.bridge import get_all_bridge_users
from sis_provisioner.dao.gws import get_uw_members, is_uw_member
from sis_provisioner.dao.pws import get_person, get_person_by_regid
from sis_provisioner.dao.user import get_all_users
from sis_provisioner.util.log import log_exception


NO_CHANGE = 0  # user exist without netid/regid change
CHANGED = 1  # changed netid or regid
LEFT_UW = 2
DISALLOWED = 3  # not personal netid


def get_validated_user(logger, uwnetid, uwregid=None, check_gws=False):
    """
    Return Person and a status
    """
    try:
        if check_gws and not is_qualified_user(logger, uwnetid):
            logger.error("%s left uw" % uwnetid)
            return None, LEFT_UW

        person = get_person(uwnetid)

        if person.uwregid is None or len(person.uwregid) == 0:
            logger.error("%s has invalid uwregid, skip!" % uwnetid)
            return None, None

        if uwregid is not None and person.uwregid != uwregid:
            return person, CHANGED

        return person, NO_CHANGE
    except DataFailureException as ex:
        if ex.status == 301:
            logger.error("%s has been changed" % uwnetid)
            if uwregid is not None:
                try:
                    person = get_person_by_regid(uwregid)
                    return person, CHANGED
                except DataFailureException as ex:
                    log_exception(
                        logger,
                        "get_person_by_regid(%s) failed, skip!" % uwregid,
                        traceback.format_exc())

        elif ex.status == 404:
            # shared or system netids
            logger.error("%s is not personal netid, skip!" % uwnetid)
            return None, DISALLOWED
        else:
            log_exception(logger,
                          "pws.get_person(%s) failed, skip!" % uwnetid,
                          traceback.format_exc())
    return None, None


def is_qualified_user(logger, uwnetid):
    try:
        return is_uw_member(uwnetid)
    except Exception:
        log_exception(logger,
                      "%s is_uw_member failed" % uwnetid,
                      traceback.format_exc())
    return False


def fetch_users_from_gws(logger):
    try:
        return get_uw_members()
    except Exception:
        log_exception(logger,
                      "Abort, failed to get uw_member from GWS",
                      traceback.format_exc())
    return None


def fetch_users_from_db(logger):
    """
    Return all the existing users in the DB
    """
    try:
        return get_all_users()
    except Exception:
        log_exception(logger,
                      "Abort, failed to get all user from DB",
                      traceback.format_exc())
    return None


def fetch_users_from_bridge(logger):
    """
    Return all the existing users in Bridge
    """
    try:
        return get_all_bridge_users()
    except Exception:
        log_exception(logger,
                      "Abort, failed to get all user from Bridge",
                      traceback.format_exc())
    return None


def get_regid_from_bridge_user(bridge_user):
    if bridge_user.custom_fields is not None and\
            len(bridge_user.custom_fields) > 0:
        for custom_field in bridge_user.custom_fields:
            if custom_field.is_regid():
                return custom_field.value
    return None
