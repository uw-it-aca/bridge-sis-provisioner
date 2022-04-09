# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging
from django.core.management.base import BaseCommand, CommandError
from sis_provisioner.dao.uw_account import get_all_uw_accounts

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    List all active users whose terminated date pass due
    """

    def handle(self, *args, **options):
        total = 0
        for uw_acc in get_all_uw_accounts():
            try:
             if uw_acc.passed_terminate_date() and not uw_acc.disabled:
                logger.info(uw_acc)
                total += 1

            except Exception as ex:
                logger.error(ex)
        logger.info("Total: {}".format(total))
