# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import re
from memcached_clients import RestclientPymemcacheClient

FIVE_SECONDS = 5
FIVE_MINS = 60 * 5
ONE_HOUR = 60 * 60
FOUR_HOURS = ONE_HOUR * 4


class BridgeAccountCache(RestclientPymemcacheClient):

    def get_cache_expiration_time(self, service, url, status=None):
        if "bridge" == service:
            if re.match(r"^/api/author/users/", url) is not None:
                return FIVE_SECONDS
            return FIVE_MINS
        if "pws" == service or "hrpws" == service:
            return FOUR_HOURS
        return ONE_HOUR
