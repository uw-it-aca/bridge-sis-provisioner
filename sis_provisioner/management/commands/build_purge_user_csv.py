import logging
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from sis_provisioner.csv_writer import CsvFileMaker
from sis_provisioner.user_loader import PurgeUserLoader


logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = 'Check for terminated users, who can be deleted now'

    def handle(self, *args, **options):
        loader = PurgeUserLoader()

        csv_maker = CsvFileMaker(loader)
        file_path = csv_maker.get_file_path()
        if file_path is None:
            print "Purge_user: Can't create CSV dir, abort."
            return

        del_user_total = csv_maker.make_delete_user_file()
        print ("Checked all %d users in DB," +
               " found %d should be deleted," +
               " and deleted %d users.") % (
            loader.get_total_count(),
            loader.get_delete_count(),
            del_user_total)

        if csv_maker.is_file_wrote():
            print "The csv file is in directory: %s\n" % file_path
