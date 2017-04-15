import logging
import traceback
from restclients.exceptions import DataFailureException,\
     InvalidNetID, InvalidRegID
from sis_provisioner.dao.bridge import get_all_bridge_users
from sis_provisioner.dao.gws import get_potential_users
from sis_provisioner.dao.pws import get_person, get_person_by_regid
from sis_provisioner.dao.user import get_all_users
from sis_provisioner.util.log import log_exception


INVALID = -3
DISALLOWED = -2  # not personal netid
LEFT_UW = -1
NO_CHANGE = 0  # no id changes
CHANGED = 1


def get_validated_user(logger, uwnetid, uwregid=None, users_in_gws=[]):
    """
    Validate an existing user in the local DB or Bridge.
    If he/she is in one of the good groups and in pws.person,
    return the corresponding Person object and a status

    raise DataFailureException if failed to access GWS or PWS
    """
    try:
        if uwregid is None:
            person = get_person(uwnetid)
        else:
            person = get_person_by_regid(uwregid)

        if person.uwnetid == uwnetid:
            if uwregid is None or person.uwregid == uwregid:

                if _user_left_uw(users_in_gws, uwnetid):
                    logger.info("user validation: %s left uw!", uwnetid)
                    return None, LEFT_UW
                return person, NO_CHANGE

        logger.info("User (%s, %s) changed netid or regid to (%s, %s)",
                    uwnetid, uwregid,
                    person.uwnetid, person.uwregid)
        return person, CHANGED

    except InvalidNetID:
        logger.error("validate_user_by_netid: %s invalid!",
                     uwnetid)
        return None, INVALID
    except InvalidRegID:
        logger.error("validate_user_by_regid: %s invalid!",
                     uwregid)
        return None, INVALID
    except DataFailureException as ex:
        if ex.status == 404:
            # shared or system netids
            logger.info("Not a personal netid: %s", uwnetid)
            return None, DISALLOWED
        log_exception(logger,
                      "validate_user (%s, %s) failed!" % (uwnetid,
                                                          uwregid),
                      traceback.format_exc())
        raise


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


def _user_left_uw(users_in_gws, uwnetid):
    return (uwnetid is not None and
            len(users_in_gws) > 0 and uwnetid not in users_in_gws)
