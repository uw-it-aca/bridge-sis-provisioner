# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging
from sis_provisioner.dao.gws import get_potential_users
from sis_provisioner.dao.pws import get_updated_persons
from sis_provisioner.util.settings import get_person_changed_window
from sis_provisioner.account_managers.gws_bridge import GwsBridgeLoader

logger = logging.getLogger(__name__)


class PwsBridgeLoader(GwsBridgeLoader):

    """
    This class will update active user accounts upon their changes in PWS
    """

    def __init__(self, worker, clogger=logger):
        super(PwsBridgeLoader, self).__init__(worker, clogger)
        self.data_source = "Person updates"

    def get_all_users(self):
        return get_potential_users()  # DataFailureException

    def fetch_users(self):
        return get_updated_persons(get_person_changed_window())

    def process_users(self):
        for person in self.get_users_to_process():
            if (self.is_invalid_person(person.uwnetid, person) or
                    not self.in_uw_groups(person.uwnetid)):
                continue
            self.total_checked_users += 1
            self.take_action(person)
