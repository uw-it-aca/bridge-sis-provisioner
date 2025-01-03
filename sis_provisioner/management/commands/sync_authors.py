# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from sis_provisioner.account_managers.author_loader import AuthorChecker
from sis_provisioner.account_managers.bridge_worker import BridgeWorker
from sis_provisioner.util.log import log_resp_time, Timer
from sis_provisioner.management.commands import send_msg


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Load authors into Bridge
    """
    def add_arguments(self, parser):
        parser.add_argument(
            "-n", "--noop", action="store_true", dest="noop", default=False,
            help="No operation")

    def handle(self, *args, **options):
        if options.get('noop'):
            return
        source = "Sync authors"
        timer = Timer()
        started = datetime.now()
        loader = AuthorChecker(BridgeWorker())
        try:
            loader.load()

            logger.info("Update {0:d} users".format(
                loader.get_updated_count()))
            if loader.has_error():
                send_msg(logger, source, loader.get_error_report())
        except Exception as ex:
            send_msg(logger, source, ex)
        finally:
            logger.info("Started at: {0}".format(started))
            log_resp_time(logger, source, timer)
