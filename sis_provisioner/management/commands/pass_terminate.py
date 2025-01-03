# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.core.management.base import BaseCommand, CommandError
from sis_provisioner.models import UwAccount, make_tz_aware


class Command(BaseCommand):
    """
    List all active users whose terminated date is before the specified
    """

    def add_arguments(self, parser):
        parser.add_argument('date-str')  # yyyy-mm-ddThh:mm

    def handle(self, *args, **options):
        tdate = make_tz_aware(options['date-str'])
        try:
            total = UwAccount.objects.exclude(disabled=True).filter(
                terminate_at__lt=tdate).count()
            print("Total users pass terminate date: {}".format(total))
        except Exception as ex:
            print(ex)
