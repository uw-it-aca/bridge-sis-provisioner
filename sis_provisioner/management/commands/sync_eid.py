# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from sis_provisioner.account_managers.eid_loader import load
from sis_provisioner.util.log import log_resp_time, Timer


logger = logging.getLogger("bridge_provisioner_commands")


class Command(BaseCommand):
    """
    Load users into Bridge
    """
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        timer = Timer()
        logger.info("Start at {0}".format(datetime.now()))
        try:
            logger.info(load())
        except Exception as ex:
            logger.error(str(ex))
        finally:
            log_resp_time(logger, "Load user EIDs", timer)
