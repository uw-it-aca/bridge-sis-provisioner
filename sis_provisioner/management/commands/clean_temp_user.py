# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging
from django.core.management.base import BaseCommand, CommandError
from sis_provisioner.dao.gws import Gws
from sis_provisioner.dao.pws import get_person

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Load users into Bridge
    """
    def add_arguments(self, parser):
        parser.add_argument('groupid')
        parser.add_argument('action',
                            choices=['all', 'purge'])

    def handle(self, *args, **options):
        groupid = options['groupid']
        action = options['action']

        gws = Gws()
        uwnetids = list(gws._get_user_set([groupid]))

        if action == 'all':
            try:
                gws.delete_members(groupid, uwnetids)
            except Exception as ex:
                logger.error(ex)
        if action == 'purge':
            for uwnetid in uwnetids:
                try:
                    if uwnetid in gws.potential_users:
                        gws.delete_members(groupid, [uwnetid])
                        continue
                    p = get_person(uwnetid)
                    if not p or p.is_test_entity:
                        gws.delete_members(groupid, [uwnetid])
                except Exception as ex:
                    logger.error(ex)
