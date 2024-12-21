# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from datetime import timedelta
import logging
from sis_provisioner.models import get_now
from django.core.management.base import BaseCommand, CommandError
from sis_provisioner.dao.bridge import BridgeUsers
from sis_provisioner.dao.gws import Gws, CUSTOM_GROUP
from sis_provisioner.dao.pws import get_person

logger = logging.getLogger(__name__)
cut_off_time = get_now() - timedelta(days=730)  # 2 years
TO_SKIP = ["u_bridgeap_tempusers-owa"]


class Command(BaseCommand):
    """
    Load users into Bridge
    """
    def add_arguments(self, parser):
        parser.add_argument('groupid')

    def handle(self, *args, **options):
        groupid = options['groupid']

        self.gws = Gws()
        if groupid == "noop":
            return
        if groupid == "all":
            self.briAcc = BridgeUsers()
            # purge memebers from all the temp user groups
            for gm in self.gws._get_members_of_group(CUSTOM_GROUP):
                if (gm.is_group() and gm.name and gm.name != TO_SKIP):
                    logger.info(f"clean_group========{gm.name}")
                    # self.clean_group(gm.name)
        else:
            # delete all the members of the specific temp user group
            uwnetids = list(self.gws._get_user_set([groupid]))
            try:
                self.gws.delete_members(groupid, uwnetids)
            except Exception as ex:
                logger.error(f"{groupid} {ex}")

    def clean_group(self, groupid):
        for uwnetid in list(self.gws._get_user_set([groupid])):
            try:
                if uwnetid in self.gws.potential_users:
                    self.gws.delete_members(groupid, [uwnetid])
                    continue
                p = get_person(uwnetid)
                if not p or p.is_test_entity:
                    self.gws.delete_members(groupid, [uwnetid])
                    continue
                bridge_acc = self.briAcc.get_user_by_uwnetid(uwnetid)
                if bridge_acc and bridge_acc.logged_in_at is None:
                    continue
                if bridge_acc and bridge_acc.logged_in_at < cut_off_time:
                    # Has mot accessed Bridge for three years
                    self.gws.delete_members(groupid, [uwnetid])
            except Exception as ex:
                logger.error(f"{groupid},{uwnetid} {ex}")
