# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from dateutil.parser import parse
from pytz import timezone
from django.test import TransactionTestCase
from django.core.management import call_command
from sis_provisioner.tests.account_managers import set_uw_account


class TestPassTerminateUser(TransactionTestCase):

    def test_pass_terminate(self):
        javerage = set_uw_account("javerage")
        javerage.set_ids(195, "123456789")
        javerage.terminate_at = timezone("US/Pacific").localize(
            parse("2022-04-01T00:01"))
        javerage.save()
        call_command('pass_terminate', "2022-04-02T00:01")
