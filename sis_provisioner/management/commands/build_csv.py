import logging
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from sis_provisioner.load_users import LoadUsers
from sis_provisioner.csv.user_writer import write_files


logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = 'Build the csv files for importing users into BridgeApp'
    args = "include-hrp (to include hrp data)"

    def handle(self, *args, **options):
        include_hrp = False
        if len(args) == 1:
            include_hrp = (args[0] == "include-hrp")

        load_users = LoadUsers(include_hrp=include_hrp)
        load_users.fetch_all()

        if load_users.get_user_count() == 0:
            print "No user found, abort!"
            return

        dir_path = write_files(load_users.get_users(),
                               include_hrp=load_users.include_hrp())
        print "The csv files are in %s\n" % dir_path
