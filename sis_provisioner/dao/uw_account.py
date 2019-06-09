"""
This module interacts with the uw bridge user table in the app's database
"""

import logging
import traceback
from sis_provisioner.models import UwAccount
from sis_provisioner.util.log import log_exception, log_resp_time, Timer


logger = logging.getLogger(__name__)


def delete_uw_account(uwnetid):
    uw_acc = get_by_netid(uwnetid)
    if uw_acc is not None:
        uw_acc.delete()


def get_all_uw_accounts():
    timer = Timer()
    action = "Fetch all users from db "
    try:
        return UwAccount.objects.all()
    except Exception:
        log_exception(logger, action, traceback.format_exc(chain=False))
    finally:
        log_resp_time(logger, action, timer)
    return []


def get_by_bridgeid(bridge_id):
    """
    @return a UwAccount objects
    @exception: UwAccount.DoesNotExist
    """
    if bridge_id > 0:
        qs = UwAccount.objects.filter(bridge_id=bridge_id)
        if len(qs) == 1:
            return qs[0]
        if len(qs) > 1:
            logger.error(
                "Multiple accounts in DB with the same bridge_id {0}".format(
                    bridge_id))
    return None


def get_by_employee_id(employee_id):
    """
    @return a UwAccount object
    @exception: UwAccount.DoesNotExist
    """
    if employee_id is not None:
        qs = UwAccount.objects.filter(employee_id=employee_id)
        if len(qs) == 1:
            return qs[0]
        if len(qs) > 1:
            logger.error(
                "Multiple accounts in DB with the same employee_id {0}".format(
                    employee_id))
    return None


def get_by_netid(uwnetid):
    """
    @return a UwAccount object
            None if not found in DB
    """
    if uwnetid is not None and UwAccount.exists(uwnetid):
        return UwAccount.get(uwnetid)
    return None


def save_uw_account(person):
    """
    :param person: Valid user
    @return 1. the UwAccount object of the account to keep
            2. a UwAccount objects of the accounts to delete
    """
    uw_account = UwAccount.get_uw_acc(person.uwnetid,
                                      person.prior_uwnetids,
                                      create=True)
    # check if there is another account of the same user
    prior_acc = None
    if len(person.prior_uwnetids) > 0:
        for prior_netid in person.prior_uwnetids:
            prior_acc = get_by_netid(prior_netid)
            if prior_acc is not None:
                # purge the prior account
                uw_account.prev_netid = prior_netid
                uw_account.save()
                prior_acc.delete()
                logger.info(
                    "{0} has two accounts in DB: KEEP {1}, DELETE {2}".format(
                        person.uwnetid, uw_account, prior_acc))
                break
    return uw_account
