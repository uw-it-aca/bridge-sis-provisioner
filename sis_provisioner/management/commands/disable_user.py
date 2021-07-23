# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from sis_provisioner.dao.bridge import BridgeUsers
from sis_provisioner.dao.pws import get_person
from sis_provisioner.dao.uw_account import get_by_netid, save_uw_account

logger = logging.getLogger("bridge_provisioner_commands")


class Command(BaseCommand):
    """
    Load users into Bridge
    """
    def add_arguments(self, parser):
        parser.add_argument('uwnetid')

    def handle(self, *args, **options):
        uwnetid = options['uwnetid']
        try:
            bridge_dao = BridgeUsers()

            uw_acc0 = get_by_netid(uwnetid)
            if uw_acc0 is not None:
                logger.info("Found existing user {}".format(uw_acc0))
                if uw_acc0.has_bridge_id():
                    bridge_acc = bridge_dao.get_user_by_bridgeid(
                        uw_acc0.bridge_id)
                    if bridge_acc is not None:
                        if bridge_acc.is_deleted():
                            if not uw_acc0.disabled:
                                uw_acc0.set_disable()
                            logger.info("Account already disabled {}".format(
                                uw_acc0))
                            return

                        if bridge_dao.delete_bridge_user(bridge_acc):
                            logger.info("DELETE {}".format(bridge_acc))
                            uw_acc0.set_disable()
                            logger.info("Disabled {}".format(uw_acc0))
                            return

            bridge_acc = bridge_dao.get_user_by_uwnetid(uwnetid)
            person = get_person(uwnetid)
            uw_acc = save_uw_account(person)
            logger.info("Matched account in DB {}".format(uw_acc))
            if bridge_acc is None:
                if uw_acc.has_prev_netid():
                    logger.info("CHANGED NETID {}".format(uw_acc))
                    bridge_acc = bridge_dao.get_user_by_uwnetid(
                        uw_acc.prev_netid)
                    if bridge_acc is not None:
                        uw_acc.set_ids(bridge_acc.bridge_id,
                                       person.employee_id)

                        bridge_acc1 = bridge_dao.change_uwnetid(uw_acc)
                        if bridge_acc1.netid == uw_acc.netid:
                            if bridge_dao.delete_bridge_user(bridge_acc1):
                                logger.info("DELETE {}".format(bridge_acc1))
                                uw_acc.set_disable()
                                logger.info("Disabled {}".format(uw_acc))
                                return
        except Exception as ex:
            logger.error(str(ex))
