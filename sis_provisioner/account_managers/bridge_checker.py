"""
This class will load all the existing users in bridge.
for those having a validate pws person, make sure it has a record in DB.
1. Add missing uw accounts into Db (manually added in Bridge).
2. If the bridge account has more than one records in DB, purge.
3. Update existing account.
"""

import logging
import traceback
from sis_provisioner.dao.bridge import (
    get_all_bridge_users, get_user_by_uwnetid)
from sis_provisioner.dao.pws import get_person, is_prior_netid
from sis_provisioner.dao.uw_account import (
    get_by_netid, save_uw_account)
from sis_provisioner.account_managers import account_not_changed
from sis_provisioner.account_managers.db_bridge import UserUpdater


logger = logging.getLogger(__name__)


class BridgeChecker(UserUpdater):

    def __init__(self, worker, clogger=logger):
        super(BridgeChecker, self).__init__(worker, clogger)

    def fetch_users(self):
        self.data_source = "Bridge"
        return get_all_bridge_users()

    def process_users(self):
        for bridge_acc in self.get_users_to_process():
            self.logger.debug("Validating Bridge user {0}".format(bridge_acc))
            uwnetid = bridge_acc.netid
            bridge_id = bridge_acc.bridge_id

            person = get_person(uwnetid)
            if person is None:
                self.add_error("Not in PWS, skip {0}".format(bridge_acc))
                # let's see what these are
                continue

            if is_prior_netid(uwnetid, person):

                exi_cur, cur_bri_acc = get_user_by_uwnetid(person.uwnetid)
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
                            "LEFT prior acc {0} UNTIL {1}".format(
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
                    uw_account.has_prev_netid() and
                    uw_account.prev_netid != bridge_acc.netid):
                self.add_error(
                    "Mis-matched accounts {0} {1}, abort update!".format(
                        bridge_acc, uw_account))
                return

            exists, bridge_acc1 = self.match_bridge_account(uw_account)
            self.logger.debug(
                "Match UW account {0} ==> Bridge account {1}".format(
                    uw_account, bridge_acc1))

            # bridge_acc and bridge_acc1
            if bridge_acc.bridge_id != bridge_acc1.bridge_id:
                self.logger.info("Merged Bridge accounts {0} TO {1}".format(
                    bridge_acc, bridge_acc1))

            uw_account.set_bridge_id(bridge_acc1.bridge_id)

            if not account_not_changed(uw_account, person, bridge_acc1):
                self.logger.info("worker.update {0}".format(uw_account))
                self.worker.update_user(bridge_acc1, uw_account, person)

        except Exception as ex:
            self.handle_exception(
                "Update Bridge account {0}".format(bridge_acc), ex, traceback)
