import logging
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from sis_provisioner.account_managers.gws_bridge import GwsBridgeLoader
from sis_provisioner.account_managers.db_bridge import UserUpdater
from sis_provisioner.account_managers.bridge_checker import BridgeChecker
from sis_provisioner.account_managers.bridge_worker import BridgeWorker


class Command(BaseCommand):
    """
    Load users into Bridge
    """
    def add_arguments(self, parser):
        parser.add_argument('data-source',
                            choices=['gws', 'db', 'bridge'])
        parser.add_argument('--include-hrp', nargs='?', default=None)

    def handle(self, *args, **options):
        source = options['data-source']
        try:
            include_hrp = options['--include-hrp'] is not None
        except KeyError:
            include_hrp = False

        if source == 'gws':
            loader = GwsBridgeLoader(BridgeWorker())
        elif source == 'db':
            loader = UserUpdater(BridgeWorker())
        elif source == 'bridge':
            loader = BridgeChecker(BridgeWorker())
        else:
            print("Invalid data source, abort!")
            return

        loader.load()

        print(datetime.now())
        print("Checked all {0:d} users in {1}\n".format(
            loader.get_total_count(), source))
        print("{0:d} new users added\n".format(loader.get_new_user_count()))
        print("{0:d} users changed netid\n".format(
            loader.get_netid_changed_count()))
        print("{0:d} users deleted\n".format(loader.get_deleted_count()))
        print("{0:d} users restored\n".format(loader.get_restored_count()))
        print("{0:d} users updated\n".format(loader.get_updated_count()))

        if loader.has_error():
            print("Errors: {0}".format(loader.get_error_report()))
