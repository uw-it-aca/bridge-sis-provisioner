# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from datetime import timedelta
import logging
import traceback
from sis_provisioner.models import get_now
from sis_provisioner.dao.pws import get_person, is_prior_netid
from sis_provisioner.dao.uw_account import get_by_netid, save_uw_account
from sis_provisioner.util.log import log_resp_time, Timer
from sis_provisioner.util.settings import get_login_window
from sis_provisioner.account_managers.acc_checker import UserAccountChecker

logger = logging.getLogger(__name__)


class BridgeChecker(UserAccountChecker):

    """
    This class will sync the daily active users in bridge,
    for those having a validate pws person, make sure it has a record in DB.
    1. Add missing uw accounts into Db (ie, manually added in Bridge).
    2. If the bridge account has more than one records in DB, purge.
    3. Update existing account.
    """

    def __init__(self, worker, clogger=logger):
        super(BridgeChecker, self).__init__(worker, clogger)
        self.data_source = "Accounts in Bridge"
        self.login_window = get_login_window()
        if self.login_window > 0:
            self.check_time = get_now() - timedelta(days=self.login_window)

    def fetch_users(self):
        timer = Timer()
        try:
            return self.get_bridge().get_all_users()
        finally:
            log_resp_time(logger, "Get all users from Bridge", timer)

    def not_accessed(self, bridge_acc):
        """
        Return True if the user has not logged on or
        has accessed Bridge prior to the login_window.
        """
        return (bridge_acc.logged_in_at is None or
                self.login_window > 0 and
                bridge_acc.logged_in_at < self.check_time)

    def process_users(self):
        for bridge_acc in self.get_users_to_process():
            if self.not_accessed(bridge_acc):
                continue

            logger.debug("Validate {0}".format(bridge_acc))
            uwnetid = bridge_acc.netid
            bridge_id = bridge_acc.bridge_id

            person = get_person(uwnetid)
            if self.is_invalid_person(uwnetid, person):
                continue

            self.total_checked_users += 1

            if is_prior_netid(uwnetid, person):

                cur_bri_acc = self.get_bridge().get_user_by_uwnetid(
                    person.uwnetid)
                if (cur_bri_acc is not None and
                        bridge_id != cur_bri_acc.bridge_id):

                    cur_uw_acc = get_by_netid(person.uwnetid)
                    if cur_uw_acc is not None:

                        uw_acc = get_by_netid(uwnetid)
                        if uw_acc is None:
                            # connect this account with that one
                            cur_uw_acc.prev_netid = uwnetid
                            cur_uw_acc.save()

                        # the current netid has another account in DB
                        # this account will be merged then.
                        self.logger.info(
                            "HOLD prior acc {0} UNTIL {1}".format(
                                bridge_acc, cur_bri_acc))
                        continue

            # 1. If bridge_acc has a current netid; otherwise
            # 2. if the one with current netid NOT exists.
            self.take_action(person, bridge_acc)

    def take_action(self, person, bridge_acc):
        """
        Make sure the Bridge user has a record in local DB
        @param person must be a valid object
        """
        try:
            uw_account = save_uw_account(person)

            if (uw_account.netid != bridge_acc.netid and
                    (uw_account.has_prev_netid() is False or
                     uw_account.prev_netid != bridge_acc.netid)):
                self.add_error(
                    "Mis-matched accounts {0} {1}, abort update!".format(
                        bridge_acc, uw_account))
                return

            bridge_acc1 = self.match_bridge_account(uw_account)
            self.logger.debug(
                "Match UW account {0} ==> Bridge account {1}".format(
                    uw_account, bridge_acc1))

            # bridge_acc and bridge_acc1 both exist
            if bridge_acc.bridge_id != bridge_acc1.bridge_id:
                self.logger.info("Merged Bridge accounts {0} TO {1}".format(
                    bridge_acc, bridge_acc1))

            uw_account.set_ids(bridge_acc1.bridge_id, person.employee_id)

            hrp_wkr = self.get_hrp_worker(person)

            if not self.account_not_changed(bridge_acc1, person, hrp_wkr):
                self.logger.debug("To update {0}, {1}".format(
                    uw_account, bridge_acc1))
                self.worker.update_user(bridge_acc1, uw_account,
                                        person, hrp_wkr)

        except Exception as ex:
            self.handle_exception(
                "Update Bridge account {0}".format(bridge_acc), ex, traceback)
