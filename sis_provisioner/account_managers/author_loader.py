# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
This class will load all the Bridge authors, check against gws author group
1. Delete former authors
2. Add new authors
"""

import logging
import traceback
from sis_provisioner.dao.gws import get_bridge_authors
from sis_provisioner.dao.pws import get_person
from sis_provisioner.dao.uw_account import save_uw_account, UwAccount
from sis_provisioner.account_managers.gws_bridge import GwsBridgeLoader

logger = logging.getLogger(__name__)


class AuthorChecker(GwsBridgeLoader):

    def __init__(self, worker, clogger=logger):
        super(AuthorChecker, self).__init__(worker, clogger)
        self.data_source = "Bridge authors"

    def fetch_users(self):
        self.cur_author_set = get_bridge_authors()
        return self.get_bridge().get_all_authors()

    def process_users(self):
        existing_bri_authors = set()
        # 1. remove former authors
        for bri_acc in self.get_users_to_process():
            self.total_checked_users += 1
            uwnetid = bri_acc.netid
            if uwnetid in self.cur_author_set:
                existing_bri_authors.add(uwnetid)
            else:
                self.remove_author_role(bri_acc)

        # 2. add new authors
        for netid in list(self.cur_author_set - existing_bri_authors):
            self.total_checked_users += 1
            if not self.known_user(netid) or not self.in_uw_groups(netid):
                continue
            self.add_author_role(netid)

    def known_user(self, uwnetid):
        return uwnetid and UwAccount.exists(uwnetid)

    def add_author_role(self, netid):
        action = "SET AUTHOR on {0}".format(netid)
        try:
            person = get_person(netid)
            if not self.is_invalid_person(netid, person):
                uw_account = save_uw_account(person)
                bridge_acc = self.match_bridge_account(uw_account)
                if bridge_acc is None or bridge_acc.netid != uw_account.netid:
                    self.add_error(
                        "New author {0}'s account NOT in Bridge!".format(
                            uw_account))
                    return
                bridge_acc.add_role(self.new_author_role())
                self.worker.update_user_role(bridge_acc)
                logger.info(action)
        except Exception as ex:
            self.handle_exception("Failed to {0} ".format(action),
                                  ex, traceback)

    def new_author_role(self):
        return self.get_bridge().user_roles.new_author_role()

    def remove_author_role(self, bridge_acc):
        action = "REMOVE AUTHOR on {0}".format(bridge_acc.netid)
        try:
            bridge_acc.delete_role(self.new_author_role())
            self.worker.update_user_role(bridge_acc)
            logger.info(action)
        except Exception as ex:
            self.handle_exception("Failed to {0}".format(action),
                                  ex, traceback)
