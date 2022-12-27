# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging
from django.core.management.base import BaseCommand, CommandError
from sis_provisioner.dao.bridge import BridgeUsers
from sis_provisioner.dao.pws import get_person
from sis_provisioner.dao.uw_account import get_by_netid, save_uw_account

logger = logging.getLogger(__name__)
bridge_dao = BridgeUsers()


class Command(BaseCommand):
    """
    Load users into Bridge
    """
    def add_arguments(self, parser):
        parser.add_argument('uwnetid')

    def handle(self, *args, **options):
        uwnetid = options['uwnetid']
        try:
            person = get_person(uwnetid)
            if person.is_test_entity:
                logger.error(
                    "{} IsTestEntity in PWS, skip!".format(uwnetid))
                return

            uw_acc = save_uw_account(person)
            logger.info("Matched account in DB: {}".format(uw_acc))

            bridge_acc = get_bridge_account(uw_acc)
            if bridge_acc is None:
                logger.error("No BridgeUsers of: {}".format(uw_acc))
                return

            if bridge_acc.is_deleted():
                buser_restored = bridge_dao.restore_bridge_user(uw_acc)
                logger.info(
                    "Restored BridgeUsers: {}".format(buser_restored))

            if uw_acc.disabled:
                uw_acc.set_restored()
                logger.info("Restored UwAccount in DB: {}".format(uw_acc))

            uw_acc.set_ids(bridge_acc.bridge_id, person.employee_id)

            if uw_acc.has_prev_netid():
                logger.info("CHANGED NETID {}".format(uw_acc))
                bridge_acc1 = bridge_dao.change_uwnetid(uw_acc)
                if bridge_acc1.netid == uw_acc.netid:
                    logger.info("Changed uwnetid {}".format(bridge_acc1))
        except Exception as ex:
            logger.error(ex)


def get_bridge_account(uw_acc):
    if uw_acc.has_bridge_id():
        return bridge_dao.get_user_by_bridgeid(uw_acc.bridge_id)
    if uw_acc.has_prev_netid():
        return bridge_dao.get_user_by_uwnetid(uw_acc.prev_netid)
    return bridge_dao.get_user_by_uwnetid(uw_acc.netid)
