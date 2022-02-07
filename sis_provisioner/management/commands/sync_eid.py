# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from sis_provisioner.account_managers.eid_loader import load
from sis_provisioner.util.log import log_resp_time, Timer

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Load users into Bridge
    """
    def add_arguments(self, parser):
        parser.add_argument(
            "-n", "--noop", action="store_true", dest="noop",
            default=False,
            help="No operation")

    def handle(self, *args, **options):
        if options.get('noop'):
            return

        timer = Timer()
        started = datetime.now()
        try:
            logger.info(load())

        except Exception as ex:
            logger.error(ex)
            raise CommandError(ex)
        finally:
            logger.info("Started at: {0}".format(started))
            log_resp_time(logger, "Sync EIDs", timer)
