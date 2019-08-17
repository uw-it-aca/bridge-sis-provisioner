"""
This class will validate the active workday user accounts in the database
against GWS groups and PWS person.
1. If the user is no longer in the specified GWS groups, schedule terminate.
2. If uw account passed the grace period for termination, disable it.
3. Update active accounts.
"""

import logging
import traceback
from sis_provisioner.dao.pws import get_person, is_prior_netid
from sis_provisioner.dao.uw_account import (
    get_all_uw_accounts, get_by_netid)
from sis_provisioner.account_managers.gws_bridge import GwsBridgeLoader


logger = logging.getLogger(__name__)


class ActiveWkrLoader(GwsBridgeLoader):

    def __init__(self, worker, clogger=logger):
        super(ActiveWkrLoader, self).__init__(worker, clogger)
        self.data_source = "DB Active-Workers"

    def fetch_users(self):
        return get_all_uw_accounts()

    def to_check(self, person):
        """
        Check only currently employed faculty, staff, affiliate, and
        student employees.
        """
        return person.is_emp_state_current()

    def process_users(self):
        """
        Process exsting users in DB, terminate those left UW and
        update those changed.
        """
        for uw_acc in self.get_users_to_process():
            self.logger.debug("Validate DB record {0}".format(uw_acc))
            uwnetid = uw_acc.netid
            person = get_person(uwnetid)
            if (self.is_invalid_person(uwnetid, person) or
                    not self.to_check(person)):
                continue

            if not uw_acc.disabled:
                self.total_checked_users += 1

                if uwnetid == person.uwnetid:
                    if self.in_uw_groups(person.uwnetid) is False:
                        self.process_termination(uw_acc)
                        continue

                if is_prior_netid(uwnetid, person):
                    cur_uw_acc = get_by_netid(person.uwnetid)
                    if (cur_uw_acc is not None and
                            cur_uw_acc.bridge_id != uw_acc.bridge_id):
                        # the current netid has another account in DB,
                        # this account will be merged then.
                        continue

                self.take_action(person, priority_changes_only=False)

    def process_termination(self, uw_acc):
        """
        @param uw_acc the UwBridgeUser object of an existing account
        Check the existing users for termination.
        If the user's termination date has been reached, disable user.
        """
        if uw_acc.has_terminate_date() is False:
            self.logger.info(
                "{0} has left UW, schedule terminate".format(uw_acc))
            uw_acc.set_terminate_date(graceful=True)
        else:
            if uw_acc.passed_terminate_date() and not uw_acc.disabled:
                self.logger.info(
                    "Passed terminate date, delete {0}".format(uw_acc))
                self.terminate_uw_account(uw_acc)

    def terminate_uw_account(self, uw_acc):
        bridge_acc1 = self.get_bridge().get_user_by_uwnetid(uw_acc.netid)
        bridge_acc2 = None
        if uw_acc.has_bridge_id():
            bridge_acc2 = self.get_bridge().get_user_by_bridgeid(
                uw_acc.bridge_id)

            if bridge_acc2 is None:
                self.add_error("{0} never existed in Bridge!".format(uw_acc))
                return

            if (bridge_acc1 is not None and
                    (bridge_acc1.bridge_id != bridge_acc2.bridge_id or
                     bridge_acc1.netid != bridge_acc2.netid)):
                self.add_error(
                    "{0} has 2 Bridge accounts {1} {2} <== {3}!".format(
                        uw_acc, bridge_acc1, bridge_acc2, "Abort deletion"))
                return
        self.execute(uw_acc, bridge_acc1, bridge_acc2)

    def execute(self, uw_acc, bridge_acc1, bridge_acc2):
        if bridge_acc1 is not None:
            if self.del_bridge_account(bridge_acc1, conditional_del=False):
                uw_acc.set_disable()
                self.logger.info("Disabled in DB: {0}".format(uw_acc))
            return
        if (bridge_acc2 is not None and bridge_acc2.is_deleted and
                uw_acc.netid == bridge_acc2.netid):
            uw_acc.set_disable()
            self.logger.info("Disabled in DB: {0}".format(uw_acc))
