import logging
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from sis_provisioner.account_managers.author_loader import AuthorChecker
from sis_provisioner.account_managers.bridge_worker import BridgeWorker
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
            loader = AuthorChecker(BridgeWorker())
            loader.load()
            logger.info("{0:d} users updated", loader.get_updated_count())
            if loader.has_error():
                logger.error("Errors: {0}".format(loader.get_error_report()))
        except Exception as ex:
            logger.error(str(ex))
        finally:
            log_resp_time(logger, "Sync authors", timer)
