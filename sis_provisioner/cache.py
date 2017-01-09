import re
from django.conf import settings
from restclients.cache_implementation import MemcachedCache, TimedCache
from restclients.exceptions import DataFailureException


FIVE_SECONDS = 5
FIFTEEN_MINS = 60 * 15
HALF_HOUR = 60 * 30
ONE_HOUR = 60 * 60
FOUR_HOURS = 60 * 60 * 4
EIGHT_HOURS = 60 * 60 * 8
ONE_DAY = 60 * 60 * 24
ONE_WEEK = 60 * 60 * 24 * 7


def get_cache_time(service, url):
    if "pws" == service or "gws" == service:
        return FOUR_HOURS

    if "bridge" == service:
        if re.match('^/api/author/custom_fields', url):
            return ONE_DAY
        else:
            return ONE_HOUR

    return FOUR_HOURS


class BridgeAccountCache(TimedCache):

    def getCache(self, service, url, headers):
        return self._response_from_cache(
            service, url, headers, get_cache_time(service, url))

    def processResponse(self, service, url, response):
        return self._process_response(service, url, response)
