import logging
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from sis_provisioner.account_managers.verify import set_bridge_ids
from sis_provisioner.dao.bridge import get_user
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
            print(datetime.now())
            print("Set bridge ids for %d users in DB" % total)

        else:
            try:
                uw_bridge_user = get_user_by_netid(uwnetid)
            except UwBridgeUser.DoesNotExist:
                print("%s is not in DB" % uwnetid)
                return
            try:
                res = get_user(uw_bridge_user.netid)
                if len(res) > 0:
                    bridge_user = res[0]
                    print("Set bridge id for %s with %s" % (uw_bridge_user,
                                                            bridge_user))
                    uw_bridge_user.set_bridge_id(bridge_user.bridge_id)
            except Exception as ex:
                print(ex)
