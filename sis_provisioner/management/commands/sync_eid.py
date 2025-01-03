# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from sis_provisioner.account_managers.eid_loader import load
from sis_provisioner.util.log import log_resp_time, Timer
from sis_provisioner.management.commands import send_msg

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
            send_msg(logger, "Sync EIDs", ex)
        finally:
            logger.info(f"Started at: {started}")
            log_resp_time(logger, "Sync EIDs", timer)
