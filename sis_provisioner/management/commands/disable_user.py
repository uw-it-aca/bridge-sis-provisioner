import logging
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from sis_provisioner.dao.bridge import BridgeUsers
from sis_provisioner.dao.uw_account import get_by_netid

logger = logging.getLogger("bridge_provisioner_commands")


class Command(BaseCommand):
    """
    Load users into Bridge
    """
    def add_arguments(self, parser):
        parser.add_argument('uwnetid')

    def handle(self, *args, **options):
        userid = options['uwnetid']
        try:
            bridge_dao = BridgeUsers()
            bridge_acc = bridge_dao.get_user_by_uwnetid(userid)
            if bridge_acc is not None:
                if bridge_dao.delete_bridge_user(bridge_acc):
                    logger.info("DELETE {}".format(bridge_acc))

                    uw_acc = get_by_netid(userid)
                    if uw_acc is not None:
                        uw_acc.set_disable()
                        logger.info("Disabled in DB {}".format(uw_acc))

        except Exception as ex:
            logger.error(str(ex))
