# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging
from datetime import datetime
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError
from sis_provisioner.account_managers.author_loader import AuthorChecker
from sis_provisioner.account_managers.bridge_worker import BridgeWorker
from sis_provisioner.util.log import log_resp_time, Timer
from sis_provisioner.util.settings import get_cronjob_sender


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Load users into Bridge
    """
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        timer = Timer()
        logger.info("Start at {0}".format(datetime.now()))
        sender = get_cronjob_sender()
        loader = AuthorChecker(BridgeWorker())
        try:
            loader.load()
        except Exception as ex:
            logger.error(ex)
            send_mail("Author Checker", "{}".format(ex), sender, [sender])
        finally:
            log_resp_time(logger, "Sync authors", timer)

        logger.info("{0:d} users updated".format(loader.get_updated_count()))
        if loader.has_error():
            err = loader.get_error_report()
            logger.error("Errors: {0}".format(err))
            send_mail("Author Checker", err, sender, [sender])
