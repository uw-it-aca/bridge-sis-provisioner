import logging
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from sis_provisioner.account_managers.verify import set_bridge_ids


class Command(BaseCommand):

    def handle(self, *args, **options):
        total = set_bridge_ids()
        print datetime.now()
        print "Set bridge ids for %d users in DB" % total
