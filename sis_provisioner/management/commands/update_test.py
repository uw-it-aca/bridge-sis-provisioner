import logging
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from sis_provisioner.dao.bridge import restore_bridge_user
from sis_provisioner.account_managers import fetch_users_from_db
from sis_provisioner.account_managers.bridge_worker import BridgeWorker


logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **options):
        total_new = 0
        total_del = 0
        total_restore = 0
        total_update = 0
        worker = BridgeWorker()

        for uw_bridge_user in fetch_users_from_db(logger):

            if uw_bridge_user.is_restore():
                total_restore += 1
                try:
                    worker.restore_user(uw_bridge_user)
                except Exception as ex:
                    print "Restore %s ==>%s" % (uw_bridge_user, ex)

            elif uw_bridge_user.passed_terminate_date():
                if not uw_bridge_user.disabled:
                    total_del += 1
                    worker.delete_user(uw_bridge_user)

            elif uw_bridge_user.is_new():
                total_new += 1
                try:
                    worker.add_new_user(uw_bridge_user)
                except Exception as ex:
                    print "Add new %s ==>%s" % (uw_bridge_user, ex)

            else:
                total_update += 1
                try:
                    worker.update_user(uw_bridge_user)
                except Exception as ex:
                    print "Update %s ==>%s" % (uw_bridge_user, ex)

        print "Total %d users to add" % total_new
        print "Added %d users" %  worker.get_new_user_count()

        print "Total %d users to delete" % total_del
        print "Added %d users" % worker.get_deleted_count()

        print "Total %d users to restore" % total_restore
        print "Added %d users" % worker.get_restored_count()

        print "NetId changed: %d" % worker.get_netid_changed_count()
        print "Regid changed: %s" % worker.get_regid_changed_count()

        print "Total %d users to update" % total_update
        print "Loaded: %d" % worker.get_loaded_count()
