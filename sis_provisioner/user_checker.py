import logging
import traceback
from restclients.exceptions import DataFailureException
from sis_provisioner.dao.pws import get_person_by_regid
from sis_provisioner.dao.user import get_all_users, set_terminate_date,\
    delete_user


logger = logging.getLogger(__name__)


def delete_terminated_users():
    """
    Check the existing users marked for termination.
    If their terminate date is reached, delete them from the DB.
    Return a list of user netids who should be removed from Bridge.
    """
    users_deleted = []
    existing_users = get_all_users()
    total = len(existing_users)
    for user in existing_users:
        if user.passed_terminate_date() and not user.no_action():
            netid_to_rm = user.netid
            netids_removed = delete_user(netid_to_rm)
            if len(netids_removed) != 1:
                logger.error("Delete user (%s) found %d records" % (
                        netid_to_rm, len(netids_removed)))
            users_deleted.append(netid_to_rm)

    logger.info("Checked %d users in DB, deleted %d users from DB" % (
            total, len(users_deleted)))
    if len(users_deleted) > 0:
        logger.info("Please remove these users from Bridge now: %s" %
                    ','.join(users_deleted))
    return total, users_deleted


def mark_terminated_users():
    """
    Check the existing users against PWS, set a termination date on
    those no longer in PWS.
    Return a list of user netids whose DB records have been marked.
    """
    users_nolonger_with_uw = []
    existing_users = get_all_users()
    total = len(existing_users)
    for user in existing_users:
        if not is_in_pws(user.regid):
            set_terminate_date(user)
            users_nolonger_with_uw.append(user.netid)

    logger.info("Checked %d users in DB, mark terminated %d user" %
                (total, len(users_nolonger_with_uw)))
    if len(users_nolonger_with_uw) > 0:
        logger.info("Terminated users who can be removed after 15 days: %s" %
                    ','.join(users_nolonger_with_uw))
    return total, users_nolonger_with_uw


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
