"""
This class will process deleted group members,
mark the user accounts in the database terminated.
Update netid if it has changed
"""

import logging
import traceback
from sis_provisioner.account_managers.gws_bridge import GwsBridgeLoader
from sis_provisioner.dao.gws import get_deleted_members
from sis_provisioner.dao.pws import get_person
from sis_provisioner.dao.uw_account import save_uw_account
from sis_provisioner.util.settings import get_group_member_del_window

logger = logging.getLogger(__name__)


class TerminateUser(GwsBridgeLoader):

    def __init__(self, worker, clogger=logger):
        super(TerminateUser, self).__init__(worker, clogger)
        self.data_source = "Group deleted member"

    def fetch_users(self):
        return list(get_deleted_members(get_group_member_del_window()))

    def process_users(self):
        for netid in self.get_users_to_process():
            person = get_person(netid)
            if self.is_invalid_person(netid, person):
                continue
            self.total_checked_users += 1
            uw_acc = save_uw_account(person, create=False)
            uwnetid = uw_acc.netid
            if (not uw_acc.disabled and
                    not uw_acc.has_terminate_date()):

                if not self.in_uw_groups(uwnetid):
                    logger.info(
                        "{0} has left UW, schedule terminate".format(uw_acc))
                    uw_acc.set_terminate_date(graceful=True)

            if uw_acc.netid_changed():
                try:
                    self.apply_change_to_bridge(uw_acc, person)
                except Exception as ex:
                    self.handle_exception(
                        "Failed to change netid {0} ".format(uwnetid),
                        ex, traceback)
