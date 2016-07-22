import logging
import traceback
from restclients.exceptions import DataFailureException
from sis_provisioner.dao.pws import get_person_by_regid
from sis_provisioner.dao.user import get_all_users, set_terminate_date


logger = logging.getLogger(__name__)


def mark_terminated_users():
    """
    Check the existing users against PWS, set a termination date on
    those no longer in PWS
    """
    users_nolonger_with_uw = []
    for user in get_all_users():
        if not is_in_pws(user.regid):
            set_terminate_date(user)
            users_nolonger_with_uw.append(user.netid)

    logger.info("mark_terminated_users: found %d user" %
                len(users_nolonger_with_uw))
    if len(users_nolonger_with_uw) > 0:
        logger.info("mark_terminated_users: these users" +
                    " will be removed in 15 days: %s" %
                    ','.join(users_nolonger_with_uw))
    return users_nolonger_with_uw


def is_in_pws(uwregid):
    try:
        p = get_person_by_regid(uwregid)
        return p is not None
    except DataFailureException as ex:
        if ex.status == 301:
            return False
        elif ex.status == 404:
            return False
        else:
            return True  # leave to next check
