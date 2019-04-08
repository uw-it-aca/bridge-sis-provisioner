import re
from django.conf import settings
from rc_django.cache_implementation import TimedCache


FIVE_SECONDS = 5
FIVE_MINS = 60 * 5
HALF_HOUR = 60 * 30
ONE_HOUR = 60 * 60
EIGHT_HOURS = 60 * 60 * 8


def get_cache_time(service, url):

    if "bridge" == service:
        if re.match(r"^/api/author/users/", url) is not None:
            return FIVE_SECONDS
        return FIVE_MINS

    if "gws" == service:
        return EIGHT_HOURS

    if "pws" == service:
        return ONE_HOUR

    return ONE_HOUR


class BridgeAccountCache(TimedCache):

    def getCache(self, service, url, headers):
        return self._response_from_cache(
            service, url, headers, get_cache_time(service, url))

    def processResponse(self, service, url, response):
        return self._process_response(service, url, response)
