import logging
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from sis_provisioner.csv_writer import CsvFileMaker
from sis_provisioner.account_managers.gws_bridge import GwsBridgeLoader
from sis_provisioner.account_managers.db_bridge import UserUpdater
from sis_provisioner.account_managers.bridge_checker import BridgeChecker
from sis_provisioner.account_managers.reload_bridge import Reloader
from sis_provisioner.account_managers.bridge_worker import BridgeWorker


class Command(BaseCommand):
    """
    Load users into Bridge
    """
    def add_arguments(self, parser):
        parser.add_argument('data-source',
                            choices=['gws', 'db', 'bridge', 'rerun'])
        parser.add_argument('--include-hrp', nargs='?', default=None)

    def handle(self, *args, **options):
        source = options['data-source']
        try:
            include_hrp = options['--include-hrp'] is not None
        except KeyError:
            include_hrp = False

        if source == 'gws':
            loader = GwsBridgeLoader(BridgeWorker(),
                                     include_hrp=include_hrp)
        elif source == 'db':
            loader = UserUpdater(BridgeWorker(),
                                 include_hrp=include_hrp)
        elif source == 'bridge':
            loader = BridgeChecker(BridgeWorker(),
                                   include_hrp=include_hrp)
        elif source == 'rerun':
            loader = Reloader(BridgeWorker(),
                              include_hrp=include_hrp)
        else:
            print "Invalid data source, abort!"
            return

        loader.load()
        print datetime.now()
        print "Checked all %d users in %s," % (loader.get_total_count(),
                                               source)
        print "total %d users loaded," % loader.get_loaded_count()
        print "%d new users added" % loader.get_new_user_count()
        print "%d users changed netid\n" % loader.get_netid_changed_count()
        print "%d users changed regid\n" % loader.get_regid_changed_count()
        print "%d users deleted\n" % loader.get_deleted_count()
        print "%d users restored\n" % loader.get_restored_count()

        if loader.has_error():
            print "Errors: %s" % loader.get_error_report()
