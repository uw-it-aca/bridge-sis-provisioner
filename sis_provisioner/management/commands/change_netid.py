import logging
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from sis_provisioner.dao.user import get_user_by_bridgeid
from sis_provisioner.account_managers.bridge_worker import BridgeWorker


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('bridge_id', type=str,
                            help="param1: bridge_id")
        parser.add_argument('netid', type=str,
                            help="param2: netid")
        parser.add_argument('old_netid', type=str,
                            help="param3: prior netid")

    def handle(self, *args, **options):
        bridge_id = options['bridge_id']
        netid = options['netid']
        old_netid = options['old_netid']

        if bridge_id:
            try:
                user = get_user_by_bridgeid(bridge_id)
            except UwBridgeUser.DoesNotExist:
                print("%s not found in DB" % bridge_id)
                return
            print("Find Bridge user by bridge_id: %s" % user)
            if user.netid != netid:
                print("Netid not match: %s %s" % (user.netid, netid))
                return
            if user.has_prev_netid() and\
               user.prev_netid == old_netid:
                pass
            else:
                user.set_prev_netid(old_netid)

            worker = BridgeWorker()
            print("Work.update %s" % user)
            worker.update_uid(user)

            print("Changed netid: %d" % worker.get_netid_changed_count())
            if worker.has_error():
                print("Errors: %s" % worker.get_error_report())
