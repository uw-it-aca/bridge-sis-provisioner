# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging
import traceback
from sis_provisioner.account_managers.gws_bridge import GwsBridgeLoader
from sis_provisioner.dao.pws import get_person
from sis_provisioner.dao.uw_account import save_uw_account
from sis_provisioner.util.settings import get_group_member_del_window

logger = logging.getLogger(__name__)


class TerminateUser(GwsBridgeLoader):

    """
    This class will process deleted group members,
    schedule terminate of the user accounts in the database.
    Update netid if it has changed
    """

    def __init__(self, worker, clogger=logger):
        super(TerminateUser, self).__init__(worker, clogger)
        self.data_source = "Group deleted member"

    def fetch_users(self):
        return list(
            self.gws.get_deleted_members(get_group_member_del_window()))

    def process_users(self):
        for netid in self.get_users_to_process():
            person = get_person(netid)
            if self.is_invalid_person(netid, person):
                continue

            uw_acc = save_uw_account(person, create=False)
            if not uw_acc or uw_acc.disabled or uw_acc.has_terminate_date():
                continue

            # existing active user to mark terminate
            self.total_checked_users += 1
            uwnetid = uw_acc.netid
            if not self.in_uw_groups(uwnetid):
                logger.info(
                    "{} has left UW, schedule terminate".format(uw_acc))
                uw_acc.set_terminate_date(graceful=True)

            if uw_acc.netid_changed():
                try:
                    self.apply_change_to_bridge(uw_acc, person)
                except Exception as ex:
                    self.handle_exception(
                        "Failed to change netid {0} ".format(uwnetid),
                        ex, traceback)
