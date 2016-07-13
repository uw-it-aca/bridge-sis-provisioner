import csv
import logging
from django.core.management.base import BaseCommand, CommandError
from sis_provisioner.load_users import LoadUsers
from sis_provisioner.csv_formatter import header_for_users, csv_for_user


logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = 'Build the csv file  for upload users into BridgeApp'
    args = "<full path file name>"

    def handle(self, *args, **options):
        if len(args) < 1:
            raise CommandError("Invalid parameter %s" % args)

        load_users = LoadUsers()
        load_users.fetch_all()

        if load_users.get_user_count() == 0:
            print "No user found, abort!"

        outfile = args[0]

        f = open(outfile, 'w')
        f.write(','.join(header_for_users()))
        f.write("\n")

        for user in load_users.get_users():
            f.write(','.join(csv_for_user(user)))
            f.write("\n")
        f.close()
