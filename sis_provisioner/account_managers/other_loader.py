# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
This class will validate all non-employee user accounts in the database
against GWS groups and PWS person.
1. If the user is no longer in the specified GWS groups, schedule terminate.
2. If uw account passed the grace period for termination, disable it.
3. Update active accounts.
"""

import logging
from sis_provisioner.account_managers.emp_loader import ActiveWkrLoader

logger = logging.getLogger(__name__)


class OtherUserLoader(ActiveWkrLoader):

    def __init__(self, worker, clogger=logger):
        super(OtherUserLoader, self).__init__(worker, clogger)
        self.data_source = "DB others"
        self.priority_changes_only = True

    def to_check(self, person):
        return not person.is_emp_state_current()
