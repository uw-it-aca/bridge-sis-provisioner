# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from datetime import datetime, timedelta
import logging
from sis_provisioner.dao.hrp import get_worker_updates
from sis_provisioner.dao.pws import get_person
from sis_provisioner.dao.uw_account import save_uw_account
from sis_provisioner.util.settings import get_worker_changed_window
from sis_provisioner.account_managers.pws_bridge import PwsBridgeLoader

logger = logging.getLogger(__name__)


class HrpBridgeLoader(PwsBridgeLoader):

    """
    This class will update user account upon the changes in HRP
    """

    def __init__(self, worker, clogger=logger):
        super(HrpBridgeLoader, self).__init__(worker, clogger)
        self.data_source = "HRP updates"

    def fetch_users(self):
        return get_worker_updates(get_worker_changed_window())

    def process_users(self):
        for worker_ref in self.get_users_to_process():
            uwnetid = worker_ref.netid
            if not self.in_uw_groups(uwnetid):
                continue
            person = get_person(uwnetid)
            if self.is_invalid_person(uwnetid, person):
                continue
            self.total_checked_users += 1
            self.take_action(person)
