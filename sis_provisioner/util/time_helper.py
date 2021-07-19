# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from datetime import date, datetime, timedelta
import pytz
from django.utils import timezone


def convert_to_tzaware_datetime(a_datetime):
    """
    @return the timezone awared datetime object for the given naive datetime
    object in current timezone.
    """
    local_tz = timezone.get_current_timezone()
    return local_tz.localize(a_datetime).astimezone(pytz.utc)
