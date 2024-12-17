# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging
from django.core.management.base import BaseCommand, CommandError
from sis_provisioner.dao.gws import Gws, CUSTOM_GROUP
from sis_provisioner.dao.pws import get_person

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Load users into Bridge
    """
    def add_arguments(self, parser):
        parser.add_argument('groupid')

    def handle(self, *args, **options):
        groupid = options['groupid']

        self.gws = Gws()
        uwnetids = list(self.gws._get_user_set([groupid]))

        if groupid == "all":
            for gm in self.gws._get_members_of_group(CUSTOM_GROUP):
                if gm.is_group() and gm.name:
                    self.clean_group(gm.name)
        else:
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
            except Exception as ex:
                logger.error(f"{groupid},{uwnetid} {ex}")
