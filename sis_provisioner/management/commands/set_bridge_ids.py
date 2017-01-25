import logging
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from sis_provisioner.account_managers.verify import set_bridge_ids
from sis_provisioner.dao.bridge import get_bridge_user_object
from sis_provisioner.dao.user import get_user_by_netid
from sis_provisioner.models import UwBridgeUser


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('netid', type=str,
                            help="param is a uwnetid or 'ALL' for all users")

    def handle(self, *args, **options):
        uwnetid = None
        uwnetid = options['netid']

        if uwnetid == 'ALL':
            total = set_bridge_ids()
            print datetime.now()
            print "Set bridge ids for %d users in DB" % total

        else:
            try:
                uw_bridge_user = get_user_by_netid(uwnetid)
            except UwBridgeUser.DoesNotExist:
                print "%s is not in DB" % uwnetid
                return
            bridge_user = get_bridge_user_object(uw_bridge_user)
            print bridge_user
            if bridge_user is not None and\
               bridge_user.netid == uw_bridge_user.netid:
                uw_bridge_user.set_bridge_id(bridge_user.bridge_id)
                print "Set bridge id for %s" % uw_bri_user
