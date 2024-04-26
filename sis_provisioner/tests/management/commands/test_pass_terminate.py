# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from dateutil.parser import parse
from django.test import TransactionTestCase
from django.core.management import call_command
from django.utils.timezone import get_default_timezone, make_aware
from sis_provisioner.tests.account_managers import set_uw_account


class TestPassTerminateUser(TransactionTestCase):

    def test_pass_terminate(self):
        dt = parse("2022-04-01T00:01")
        javerage = set_uw_account("javerage")
        javerage.set_ids(195, "123456789")
        javerage.terminate_at = make_aware(dt, get_default_timezone())
        javerage.save()
        call_command('pass_terminate', "2022-04-02")
