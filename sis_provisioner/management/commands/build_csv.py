import logging
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from sis_provisioner.csv_writer import CsvFileMaker


logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = 'Build the csv files for importing users into BridgeApp'
    args = "include-hrp (to include hrp data)"

    def handle(self, *args, **options):
        include_hrp = False
        if len(args) == 1:
            include_hrp = (args[0] == "include-hrp")

        csv_maker = CsvFileMaker(include_hrp=include_hrp)
        file_path = csv_maker.get_file_path()
        if file_path is None:
            print "Cannot create CSV dir, abort."
            return

        add_user_total = csv_maker.make_add_user_files()
        del_user_total = csv_maker.make_delete_user_file()
        netid_changed_user_total = csv_maker.make_netid_change_user_file()
        regid_changed_user_total = csv_maker.make_regid_change_user_file()

        print "%d users to add\n" % add_user_total
        print "%d users to delete\n" % del_user_total
        print "%d users changed netid\n" % netid_changed_user_total
        print "%d users changed regid\n" % regid_changed_user_total
        print "The csv files are in %s\n" % csv_maker.get_file_path()
