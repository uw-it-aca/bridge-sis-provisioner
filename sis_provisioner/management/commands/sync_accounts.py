# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from sis_provisioner.account_managers.gws_bridge import GwsBridgeLoader
from sis_provisioner.account_managers.emp_loader import ActiveWkrLoader
from sis_provisioner.account_managers.other_loader import OtherUserLoader
from sis_provisioner.account_managers.bridge_checker import BridgeChecker
from sis_provisioner.account_managers.bridge_worker import BridgeWorker
from sis_provisioner.account_managers.pws_bridge import PwsBridgeLoader
from sis_provisioner.account_managers.hrp_bridge import HrpBridgeLoader
from sis_provisioner.util.log import log_resp_time, Timer


logger = logging.getLogger("bridge_provisioner_commands")


class Command(BaseCommand):
    """
    Load users into Bridge
    """
    def add_arguments(self, parser):
        parser.add_argument('data-source',
                            choices=['gws', 'db-emp', 'db-other',
                                     'bridge', 'hrp', 'pws'])

    def handle(self, *args, **options):
        timer = Timer()
        logger.info("Start at {0}".format(datetime.now()))

        source = options['data-source']
        workr = BridgeWorker()
        if source == 'gws':
            loader = GwsBridgeLoader(workr)
        elif source == 'db-emp':
            loader = ActiveWkrLoader(workr)
        elif source == 'db-other':
            loader = OtherUserLoader(workr)
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
            logger.error(str(ex))

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
            logger.error("Errors: {0}".format(loader.get_error_report()))
