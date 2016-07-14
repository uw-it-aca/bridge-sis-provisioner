import logging
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from sis_provisioner.load_users import LoadUsers
from sis_provisioner.csv.user_writer import write_files


logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = 'Build the csv files for importing users into BridgeApp'

    def handle(self, *args, **options):
        load_users = LoadUsers()
        load_users.fetch_all()

        if load_users.get_user_count() == 0:
            print "No user found, abort!"
            return

        dir_path = write_files(load_users.get_users())
        print "The csv files are in %s\n" % dir_path
