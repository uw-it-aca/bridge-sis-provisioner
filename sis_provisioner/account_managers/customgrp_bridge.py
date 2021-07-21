"""
This class will validate all non-employee user accounts in the database
against GWS groups and PWS person.
1. If the user is no longer in the specified GWS groups, schedule terminate.
2. If uw account passed the grace period for termination, disable it.
3. Update active accounts.
"""

import logging
from sis_provisioner.account_managers.gws_bridge import GwsBridgeLoader
from sis_provisioner.dao.gws import get_additional_users

logger = logging.getLogger(__name__)


class CustomGroupLoader(GwsBridgeLoader):

    def __init__(self, worker, clogger=logger):
        super(CustomGroupLoader, self).__init__(worker, clogger)
        self.data_source = "Custom group"

    def fetch_users(self):
        return list(get_additional_users())
