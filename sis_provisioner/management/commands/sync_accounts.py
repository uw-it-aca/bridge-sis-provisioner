# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging
from datetime import datetime
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError
from sis_provisioner.account_managers.gws_bridge import GwsBridgeLoader
from sis_provisioner.account_managers.acc_checker import UserAccountChecker
from sis_provisioner.account_managers.terminate import TerminateUser
from sis_provisioner.account_managers.bridge_checker import BridgeChecker
from sis_provisioner.account_managers.bridge_worker import BridgeWorker
from sis_provisioner.account_managers.pws_bridge import PwsBridgeLoader
from sis_provisioner.account_managers.hrp_bridge import HrpBridgeLoader
from sis_provisioner.account_managers.customgrp_bridge import CustomGroupLoader
from sis_provisioner.util.log import log_resp_time, Timer
from sis_provisioner.util.settings import get_cronjob_sender


logger = logging.getLogger("bridge_provisioner_commands")


class Command(BaseCommand):
    """
    Load users into Bridge
    """
    def add_arguments(self, parser):
        parser.add_argument('data-source',
                            choices=['gws', 'db-acc', 'delete',
                                     'bridge', 'hrp', 'pws', 'customg'])

    def handle(self, *args, **options):
        timer = Timer()
        logger.info("Start at {0}".format(datetime.now()))
        sender = get_cronjob_sender()
        source = options['data-source']
        workr = BridgeWorker()
        if source == 'gws':
            loader = GwsBridgeLoader(workr)
        elif source == 'customg':
            loader = CustomGroupLoader(workr)
        elif source == 'db-acc':
            loader = UserAccountChecker(workr)
        elif source == 'delete':
            loader = TerminateUser(workr)
        elif source == 'bridge':
            loader = BridgeChecker(workr)
        elif source == 'pws':
            loader = PwsBridgeLoader(workr)
        elif source == 'hrp':
            loader = HrpBridgeLoader(workr)
        else:
            logger.info("Invalid data source, abort!")
            return
        try:
            loader.load()
        except Exception as ex:
            logger.error(ex)
            send_mail("Check source: {}".format(source),
                      "{}".format(ex), sender, [sender])

        log_resp_time(logger, "Load users", timer)

        logger.info("Checked {0:d} users, source: {1}\n".format(
            loader.get_total_checked_users(), source))

        logger.info("{0:d} new users added\n".format(
            loader.get_new_user_count()))
        logger.info("{0:d} users changed netid\n".format(
            loader.get_netid_changed_count()))
        logger.info("{0:d} users deleted\n".format(
            loader.get_deleted_count()))
        logger.info("{0:d} users restored\n".format(
            loader.get_restored_count()))
        logger.info("{0:d} users updated\n".format(
            loader.get_updated_count()))

        if loader.has_error():
            err = loader.get_error_report()
            logger.error("Errors: {0}".format(err))
            send_mail("Check source: {}".format(source),
                      err, sender, [sender])
