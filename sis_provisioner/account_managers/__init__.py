import logging
import traceback
from restclients.exceptions import DataFailureException
from sis_provisioner.dao.bridge import get_all_bridge_users
from sis_provisioner.dao.gws import get_potential_users, is_qualified_user
from sis_provisioner.dao.pws import get_person, get_person_by_regid
from sis_provisioner.dao.user import get_all_users
from sis_provisioner.util.log import log_exception


NO_CHANGE = 0  # user exist without netid/regid change
CHANGED = 1  # changed netid or regid
LEFT_UW = 2
DISALLOWED = 3  # not personal netid


def get_validated_user(logger, uwnetid, uwregid=None, check_gws=False):
    """
    Validate an existing user in the local DB or Bridge.
    If he/she is in one of the good groups and in pws.person,
    return the corresponding Person object and a status

    raise DataFailureException if failed to access GWS or PWS
    """
    if check_gws and not is_qualified_user(uwnetid):
        logger.error("user validation: %s has left uw!" % uwnetid)
        return None, LEFT_UW

    try:
        person = get_person(uwnetid)

        if person.uwregid is None or len(person.uwregid) == 0:
            logger.error("%s has invalid uwregid in PWS.Person!" % uwnetid)
            return None, None

        if uwregid is not None and person.uwregid != uwregid:
            return person, CHANGED

        return person, NO_CHANGE
    except DataFailureException as ex:
        if ex.status == 301:
            # netid changed
            logger.error(
                "user validation: %s (301) netid has changed!" % uwnetid)
            if uwregid is not None:
                try:
                    person = get_person_by_regid(uwregid)
                    return person, CHANGED
                except DataFailureException as ex:
                    log_exception(
                        logger,
                        "user validation: (%s, %s) failed!" % (uwnetid,
                                                               uwregid),
                        traceback.format_exc())

        elif ex.status == 404:
            # shared or system netids
            logger.error(
                "user validation: %s is not a personal netid!" % uwnetid)
            return None, DISALLOWED
        else:
            raise
    return None, None


def fetch_users_from_gws(logger):
    try:
        return get_potential_users()
    except Exception:
        log_exception(logger,
                      "Failed to fetch_users_from_gws:",
                      traceback.format_exc())
    return []


def fetch_users_from_db(logger):
    """
    Return a list of UwBridgeUser objects of
    all the existing users in the DB
    """
    try:
        return get_all_users()
    except Exception:
        log_exception(logger,
                      "Failed to fetch_users_from_db:",
                      traceback.format_exc())
    return []


def fetch_users_from_bridge(logger):
    """
    Return a list of BridgeUser objects of
    all the existing active users in Bridge
    """
    try:
        return get_all_bridge_users()
    except Exception:
        log_exception(logger,
                      "Failed to fetch_users_from_bridge:",
                      traceback.format_exc())
    return []


def get_regid_from_bridge_user(bridge_user):
    if bridge_user.custom_fields is not None and\
            len(bridge_user.custom_fields) > 0:
        for custom_field in bridge_user.custom_fields:
            if custom_field.is_regid():
                return custom_field.value
    return None