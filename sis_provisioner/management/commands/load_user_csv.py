import logging
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from sis_provisioner.csv_writer import CsvFileMaker
from sis_provisioner.account_managers.gws_bridge import GwsBridgeLoader
from sis_provisioner.account_managers.db_bridge import UserUpdater
from sis_provisioner.account_managers.bridge_checker import BridgeChecker
from sis_provisioner.account_managers.csv_worker import CsvWorker


class Command(BaseCommand):
    """
    Build the csv files for importing users into Bridge
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
            loader = GwsBridgeLoader(CsvWorker(),
                                     include_hrp=include_hrp)
        elif source == 'db':
            loader = UserUpdater(CsvWorker(),
                                 include_hrp=include_hrp)
        elif source == 'bridge':
            loader = BridgeChecker(CsvWorker(),
                                   include_hrp=include_hrp)
        else:
            print("Invalid data source, abort!")
            return

        csv_maker = CsvFileMaker(loader, include_hrp=include_hrp)
        file_path = csv_maker.get_file_path()
        if file_path is None:
            print("Load_user_csv: Can't create CSV dir, abort.")
            return

        load_user_total = csv_maker.make_load_user_files()
        netid_changed_user_total = csv_maker.make_netid_change_user_file()
        regid_changed_user_total = csv_maker.make_regid_change_user_file()
        del_user_total = csv_maker.make_delete_user_file()
        restored_user_total = csv_maker.make_restore_user_file()
        print(datetime.now())
        print("Checked all %d users in %s," % (loader.get_total_count(),
                                               source))
        print("%d users to load\n" % load_user_total)
        print("%d users changed netid\n" % netid_changed_user_total)
        print("%d users changed regid\n" % regid_changed_user_total)
        print("%d users to be deleted\n" % del_user_total)
        print("%d users to be restored\n" % restored_user_total)

        if csv_maker.is_file_wrote():
            print("The csv files are in directory: %s\n" % file_path)
