from datetime import date, datetime, timedelta
import pytz
from django.utils import timezone
from restclients.util.timer import Timer


def convert_to_tzaware_datetime(a_datetime):
    """
    @return the timezone awared datetime object for the given naive datetime
    object in current timezone.
    """
    local_tz = timezone.get_current_timezone()
    return local_tz.localize(a_datetime).astimezone(pytz.utc)
