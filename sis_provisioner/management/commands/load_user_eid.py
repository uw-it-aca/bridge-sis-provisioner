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
        pass

    def handle(self, *args, **options):
        timer = Timer()
        print("Start at {0}".format(datetime.now()))
        try:
            total_count = load()
        except Exception as ex:
            logger.error(str(ex))
        finally:
            log_resp_time(logger, "Load user EIDs", timer)

        logger.info("Total user synced eid: {0:d}\n".format(total_count))
