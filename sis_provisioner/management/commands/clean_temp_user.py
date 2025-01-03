# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from datetime import timedelta
import logging
from sis_provisioner.dao import DataFailureException
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
                if (gm.is_group() and gm.name and gm.name not in TO_SKIP):
                    self.clean_group(gm.name)
        else:
            # delete all the members of the specific temp user group
            uwnetids = list(self.gws._get_user_set([groupid]))
            try:
                self.gws.delete_members(groupid, uwnetids)
            except Exception as ex:
                logger.error(f"{groupid} {ex}")

    def clean_group(self, groupid):
        total_removed = 0
        for uwnetid in list(self.gws._get_user_set([groupid])):
            try:
                if uwnetid in self.gws.base_users:
                    logger.info(f"{uwnetid} is base user, remove")
                    self.gws.delete_members(groupid, [uwnetid])
                    total_removed += 1
                    continue

                p = get_person(uwnetid)
                if not p:
                    logger.info(f"{uwnetid} no pws.Person, remove")
                    self.gws.delete_members(groupid, [uwnetid])
                    total_removed += 1
                    continue

                bridge_acc = self.briAcc.get_user_by_uwnetid(uwnetid)
                if not bridge_acc:
                    logger.info(f"{uwnetid} not in Bridge")
                    continue

                if bridge_acc.logged_in_at is None:
                    # Has mot used Bridge yet
                    logger.info(f"{uwnetid} never accessed Bridge")
                    continue

                if bridge_acc.logged_in_at < cut_off_time:
                    logger.info(
                        f"{uwnetid} last login: {bridge_acc.logged_in_at}" +
                        f" before {cut_off_time}")
                    self.gws.delete_members(groupid, [uwnetid])
                    total_removed += 1
            except Exception as ex:
                logger.error(f"{groupid},{uwnetid} {ex}")

        logger.info(f"{groupid} removed {total_removed} members")
