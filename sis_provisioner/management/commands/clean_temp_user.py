# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging
from django.core.management.base import BaseCommand, CommandError
from sis_provisioner.dao.gws import (
  gws, get_members_of_group, append_netids_userset)
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
        uwnetids = set()
        members = get_members_of_group(groupid)
        append_netids_userset(members, uwnetids)
        if action == 'all':
            try:
                gws.delete_members(groupid, list(uwnetids))
            except Exception as ex:
                logger.error(ex)
        if action == 'purge':
            try:
                for uwnetid in list(uwnetids):
                    p = get_person(uwnetid)
                    if p.is_emp_state_current() or p.is_stud_state_current():
                        gws.delete_members(groupid, [uwnetid])
            except Exception as ex:
                logger.error(ex)
