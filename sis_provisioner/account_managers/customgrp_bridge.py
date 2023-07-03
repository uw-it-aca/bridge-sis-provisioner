# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging
from sis_provisioner.account_managers.gws_bridge import GwsBridgeLoader
from sis_provisioner.dao.gws import get_additional_users

logger = logging.getLogger(__name__)


class CustomGroupLoader(GwsBridgeLoader):
    """
    This class will validate custom group members
    1. If the user is not in DB, add to Bridge
    2. Update active accounts.
    """

    def __init__(self, worker, clogger=logger):
        super(CustomGroupLoader, self).__init__(worker, clogger)
        self.data_source = "Custom group"

    def update_existing_accs(self):
        return False

    def fetch_users(self):
        return list(get_additional_users())
