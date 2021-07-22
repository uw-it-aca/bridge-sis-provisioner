"""
This class will validate custom group members
1. If the user is not in DB, add to Bridge
2. Update active accounts.
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
