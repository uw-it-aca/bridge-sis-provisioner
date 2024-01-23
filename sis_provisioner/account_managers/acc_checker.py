# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging
import traceback
from sis_provisioner.dao.pws import get_person, is_prior_netid
from sis_provisioner.dao.uw_account import (
    get_all_uw_accounts, get_by_netid)
from sis_provisioner.util.settings import check_all_accounts
from sis_provisioner.account_managers.gws_bridge import GwsBridgeLoader

logger = logging.getLogger(__name__)
MAX_DELETION = 40000


class UserAccountChecker(GwsBridgeLoader):

    """
    This class will validate the user accounts in the database
    against GWS groups, HRP and PWS person.
    1. Schedule terminate if the user left the groups
    2. If uw account passed the grace period for termination, disable it
    3. Restore account
    4. Update active accounts.
    """

    def __init__(self, worker, clogger=logger):
        super(UserAccountChecker, self).__init__(worker, clogger)
        self.data_source = "Accounts in DB"
        self.total_deleted = 0

    def fetch_users(self):
        return get_all_uw_accounts()

    def to_check(self, person):
        """
        Check only currently employed faculty, staff, affiliate, and
        student employees.
        """
        return check_all_accounts() or person.is_emp_state_current()

    def process_users(self):
        """
        Process exsting users in DB, terminate those left UW and
        update those changed.
        """
        for uw_acc in self.get_users_to_process():
            self.logger.debug("Validate {0}".format(uw_acc))
            self.total_checked_users += 1
            person = get_person(uw_acc.netid)

            if person is None:
                # Skip this account in case PWS unavailable
                continue

            if (not self.in_uw_groups(person.uwnetid) or
                    person.is_test_entity):
                if not uw_acc.disabled:
                    self.process_termination(uw_acc)
                continue

            if not self.to_check(person):
                continue

            if uw_acc.disabled and uw_acc.netid == person.uwnetid:
                bridge_acc = self.worker.restore_user(uw_acc)
                if bridge_acc is None:
                    self.add_error("Failed to restore {0}".format(uw_acc))
                    continue
                uw_acc.set_ids(bridge_acc.bridge_id, person.employee_id)

            if is_prior_netid(uw_acc.netid, person):
                cur_uw_acc = get_by_netid(person.uwnetid)
                if (cur_uw_acc is not None and
                        cur_uw_acc.bridge_id != uw_acc.bridge_id):
                    # the current netid has another account in DB,
                    # this account will be merged then.
                    continue

            self.take_action(person)

    def process_termination(self, uw_acc):
        """
        @param uw_acc the UwBridgeUser object of an existing account
        Check the existing users for termination.
        If the user's termination date has been reached, disable user.
        """
        if not uw_acc.has_terminate_date():
            # Left UW, schedule terminate
            uw_acc.set_terminate_date(graceful=True)
        else:
            if (uw_acc.passed_terminate_date() and not uw_acc.disabled and
                    self.total_deleted < MAX_DELETION):
                # Passed terminate date, to delete
                self.terminate_uw_account(uw_acc)

    def terminate_uw_account(self, uw_acc):
        bridge_acc1 = self.get_bridge().get_user_by_uwnetid(uw_acc.netid)
        bridge_acc2 = None
        if uw_acc.has_bridge_id():
            bridge_acc2 = self.get_bridge().get_user_by_bridgeid(
                uw_acc.bridge_id)
            if (bridge_acc1 and bridge_acc2 and
                    (bridge_acc1.bridge_id != bridge_acc2.bridge_id or
                     bridge_acc1.netid != bridge_acc2.netid)):
                self.add_error(
                    "{0} has 2 Bridge accounts {1} {2} <== {3}!".format(
                        uw_acc, bridge_acc1, bridge_acc2, "Abort deletion"))
                return

        self.execute(uw_acc, bridge_acc1, bridge_acc2)

    def execute(self, uw_acc, bridge_acc1, bridge_acc2):
        if bridge_acc1 and not bridge_acc1.is_deleted():
            if self.del_bridge_account(bridge_acc1, conditional_del=False):
                self.total_deleted += 1
                uw_acc.set_disable()
                self.logger.info("Disabled in DB: {0}".format(uw_acc))
            return
        if (bridge_acc1 and bridge_acc1.is_deleted() or
                bridge_acc2 and bridge_acc2.is_deleted() and
                uw_acc.netid == bridge_acc2.netid):
            uw_acc.set_disable()
            self.logger.info("Disabled in DB: {0}".format(uw_acc))
