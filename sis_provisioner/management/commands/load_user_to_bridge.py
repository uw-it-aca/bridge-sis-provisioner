import logging
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from sis_provisioner.account_managers.gws_bridge import GwsBridgeLoader
from sis_provisioner.account_managers.db_bridge import UserUpdater
from sis_provisioner.account_managers.bridge_checker import BridgeChecker
from sis_provisioner.account_managers.bridge_worker import BridgeWorker
from sis_provisioner.util.log import log_resp_time, Timer


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Load users into Bridge
    """
    def add_arguments(self, parser):
        parser.add_argument('data-source',
                            choices=['gws', 'db', 'bridge'])

    def handle(self, *args, **options):
        timer = Timer()
        print("Start at {0}".format(datetime.now()))

        source = options['data-source']
        if source == 'gws':
            loader = GwsBridgeLoader(BridgeWorker())
        elif source == 'db':
            loader = UserUpdater(BridgeWorker())
        elif source == 'bridge':
            loader = BridgeChecker(BridgeWorker())
        else:
            print("Invalid data source, abort!")
            return
        try:
            loader.load()
        except Exception as ex:
            print(str(ex))

        log_resp_time(logger, "Load users", timer)

        print("Checked {0:d} users, source: {1}\n".format(
            loader.get_total_count(), source))

        print("{0:d} new users added\n".format(loader.get_new_user_count()))
        print("{0:d} users changed netid\n".format(
            loader.get_netid_changed_count()))
        print("{0:d} users deleted\n".format(loader.get_deleted_count()))
        print("{0:d} users restored\n".format(loader.get_restored_count()))
        print("{0:d} users updated\n".format(loader.get_updated_count()))

        if loader.has_error():
            print("Errors: {0}".format(loader.get_error_report()))
