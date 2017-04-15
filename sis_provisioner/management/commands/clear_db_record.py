import logging
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from sis_provisioner.dao.pws import is_moved_regid, is_moved_netid
from sis_provisioner.dao.user import get_user_by_netid, get_user_by_regid
from sis_provisioner.models import UwBridgeUser


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('regid', type=str,
                            help="param1: regid")
        parser.add_argument('netid', type=str,
                            help="param2: netid")

    def handle(self, *args, **options):
        regid = options['regid']
        netid = options['netid']

        if regid:
            try:
                user = get_user_by_regid(regid)
                print "Find Bridge user by regid: %s" % user
                if is_moved_regid(regid):
                    user.delete()
                    print "Deleted it from DB!"
            except UwBridgeUser.DoesNotExist:
                print "%s not found in DB" % regid

        if netid:
            try:
                user = get_user_by_netid(netid)
                print "Find Bridge user by netid: %s" % user
                if is_moved_netid(netid):
                    user.delete()
                    print "Deleted it from DB!"
            except UwBridgeUser.DoesNotExist:
                print "%s not found in DB" % netid
