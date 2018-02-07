import logging
import traceback
from restclients_core.exceptions import DataFailureException,\
     InvalidNetID, InvalidRegID
from sis_provisioner.dao.bridge import get_all_bridge_users
from sis_provisioner.dao.gws import get_potential_users
from sis_provisioner.dao.pws import get_person, get_person_by_regid
from sis_provisioner.dao.user import get_all_users
from sis_provisioner.util.log import log_exception


INVALID = -2  # netid or regid itself is invalid
DISALLOWED = -1  # not a personal netid or regid
LEFT_UW = 0   # netid and regid are up-to-date and no longer with UW
VALID = 1     # netid and regid are up-to-date (match with Person)
CHANGED = 2   # netid or regid or both changed


def get_validated_user(logger, uwnetid, uwregid=None, users_in_gws=[]):
    """
    Validate an existing user.
    return the corresponding Person object and a status
    raise DataFailureException if failed to access GWS or PWS
    """
    try:
        if uwregid is None:
            person = get_person(uwnetid)
        else:
            person = get_person_by_regid(uwregid)

        # changed takes priority over left UW
        if person.uwnetid != uwnetid:
            return person, CHANGED

        if uwregid is not None and person.uwregid != uwregid:
            return person, CHANGED

        if _user_left_uw(users_in_gws, uwnetid):
            logger.info("validate '%s' has left uw!", uwnetid)
            return person, LEFT_UW

        return person, VALID

    except InvalidNetID:
        logger.error("validate_by_netid: '%s' invalid!",
                     uwnetid)
        return None, INVALID
    except InvalidRegID:
        logger.error("validate_by_regid: '%s' invalid!",
                     uwregid)
        return None, INVALID
    except DataFailureException as ex:
        if ex.status == 404:
            # shared or system netids
            logger.info("validate ('%s', %s) not personal netid/regid",
                        uwnetid, uwregid)
            return None, DISALLOWED
        log_exception(logger,
                      "validate ('%s', %s) failed, skip!" % (uwnetid,
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
