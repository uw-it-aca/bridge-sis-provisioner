import logging
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from sis_provisioner.dao.pws import get_person
from sis_provisioner.models import UwAccount, UwBridgeUser


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Load users into Bridge
    """
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        total_count = 0
        users = UwBridgeUser.objects.all()
        print("Start at {0} to migrate {1:d} records".format(
            datetime.now(), len(users)))
        for old_acc in users:
            try:
                uwnetid = old_acc.netid
                person = get_person(uwnetid)
                if person is None:
                    # not a valid netid
                    print("Not found in PWS, skip {0}!".format(old_acc))
                    continue

                if UwAccount.exists(uwnetid) is False:
                    UwAccount.objects.create(
                        bridge_id=old_acc.bridge_id,
                        netid=old_acc.netid,
                        prev_netid=old_acc.prev_netid,
                        disabled=old_acc.disabled,
                        last_updated=old_acc.last_visited_at,
                        terminate_at=old_acc.terminate_at)
                    total_count += 1
            except Exception as ex:
                print("Copy {0} ==> {1}".format(old_acc, str(ex)))
        print("Finished copy of {0:d} records at {1}\n".format(
            total_count, datetime.now()))
