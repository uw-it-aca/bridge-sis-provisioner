import logging
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from sis_provisioner.csv_writer import CsvFileMaker
from sis_provisioner.user_checker import PurgeUserLoader


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
        print "Checked all %d users in DB," % loader.get_total_count()
        print "Found %d users left UW," % loader.get_users_left_uw_count()
        print "Deleted %d users from DB," % loader.get_delete_count()
        print "%d users should be remove from Bridge asap." % del_user_total

        if csv_maker.is_file_wrote():
            print "The csv file is in directory: %s\n" % file_path
