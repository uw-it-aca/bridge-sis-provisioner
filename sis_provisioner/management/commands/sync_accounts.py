# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging
from datetime import datetime
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError
from sis_provisioner.dao import is_using_file_dao
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


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Load users into Bridge
    """
    def add_arguments(self, parser):
        parser.add_argument('data-source',
                            choices=['gws', 'db-acc', 'delete',
                                     'bridge', 'hrp', 'pws', 'customg'])

    def handle(self, *args, **options):
        self.timer = Timer()
        logger.info("Start at {0}".format(datetime.now()))
        self.sender = get_cronjob_sender()
        self.source = options['data-source']
        workr = BridgeWorker()
        if self.source == 'gws':
            self.loader = GwsBridgeLoader(workr)
        elif self.source == 'customg':
            self.loader = CustomGroupLoader(workr)
        elif self.source == 'db-acc':
            self.loader = UserAccountChecker(workr)
        elif self.source == 'delete':
            self.loader = TerminateUser(workr)
        elif self.source == 'bridge':
            self.loader = BridgeChecker(workr)
        elif self.source == 'pws':
            self.loader = PwsBridgeLoader(workr)
        elif self.source == 'hrp':
            self.loader = HrpBridgeLoader(workr)
        else:
            logger.info("Invalid data source, abort!")
            return
        try:
            self.loader.load()
            self.log_msg()
        except Exception as ex:
            msg = {"Source": self.source, "Error": ex}
            logger.error(msg)
            send_mail(self.source, msg, self.sender, [self.sender])
            # raise CommandError(ex)

    def log_msg(self):
        log_resp_time(logger, "Load users", self.timer)

        logger.info("Checked {0:d} users, source: {1}\n".format(
            self.loader.get_total_checked_users(), self.source))

        logger.info("{0:d} new users added\n".format(
            self.loader.get_new_user_count()))
        logger.info("{0:d} users changed netid\n".format(
            self.loader.get_netid_changed_count()))
        logger.info("{0:d} users deleted\n".format(
            self.loader.get_deleted_count()))
        logger.info("{0:d} users restored\n".format(
            self.loader.get_restored_count()))
        logger.info("{0:d} users updated\n".format(
            self.loader.get_updated_count()))

        if self.loader.has_error():
            msg = {
                "Source": self.source,
                "Error": self.loader.get_error_report()
            }
            logger.error(msg)
            if not is_using_file_dao():
                try:
                    send_mail(
                        f"Check source: {self.source}", msg,
                        self.sender, [self.sender]]
                    )
                except Exception as ex:
                    exmsg = {"Source": self.source, "Error": ex}
                    logger.error(exmsg)
