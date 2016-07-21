import logging
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from sis_provisioner.user_checker import mark_terminated_users


logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = 'Check existing users and mark those no longer affiliated with UW'

    def handle(self, *args, **options):
        users_nolonger_with_uw = mark_terminated_users()
        print "Check terminated users: found %d users" %\
            len(users_nolonger_with_uw)
        if len(users_nolonger_with_uw) > 0:
            print "These users can be removed in 15 days: %s" %\
                ','.join(users_nolonger_with_uw)
