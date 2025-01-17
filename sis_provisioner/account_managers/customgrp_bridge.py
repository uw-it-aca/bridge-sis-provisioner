# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging
import traceback
from sis_provisioner.dao.pws import get_person
from sis_provisioner.account_managers.gws_bridge import GwsBridgeLoader
from sis_provisioner.util.log import log_exception

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
        user_list = []
        for uwnetid in list(self.gws.temp_user_set):
            try:
                p = get_person(uwnetid)
                if (self.is_invalid_person(uwnetid, p) or
                        uwnetid in self.gws.base_users):
                    continue
                user_list.append(uwnetid)
            except Exception:
                log_exception(
                    logger, f"get_person_by_netid({uwnetid})",
                    traceback.format_exc(chain=False)
                )
        return user_list
