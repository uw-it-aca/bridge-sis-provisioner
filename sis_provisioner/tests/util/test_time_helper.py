# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.conf import settings
from django.test import TestCase
from datetime import datetime
from sis_provisioner.util.time_helper import convert_to_tzaware_datetime


class TestTimeHelper(TestCase):

    def test_convert(self):
        dt = datetime(2016, 7, 12, 0, 0, 1)
        tz_dt = convert_to_tzaware_datetime(dt)
        self.assertEqual(str(tz_dt), '2016-07-12 07:00:01+00:00')

        dt = datetime(2016, 2, 12, 0, 0, 1)
        tz_dt = convert_to_tzaware_datetime(dt)
        self.assertEqual(str(tz_dt), '2016-02-12 08:00:01+00:00')
