# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase
from sis_provisioner.cache import BridgeAccountCache
from sis_provisioner.tests import fdao_gws_override

CACHE = 'sis_provisioner.cache.BridgeAccountCache'
FIVE_SECONDS = 5
FIVE_MINS = 60 * 5
ONE_HOUR = 60 * 60
FOUR_HOURS = 60 * 60 * 4


@fdao_gws_override
class TestCachePolicy(TestCase):

    def test_get_cache_time(self):
        cache = BridgeAccountCache()
        self.assertEquals(
            cache.get_cache_expiration_time("gws", "/group_sws/v3/group/"),
            ONE_HOUR)
        self.assertEquals(
            cache.get_cache_expiration_time("pws", "/identity/v2/person/"),
            FOUR_HOURS)
        self.assertEquals(
            cache.get_cache_expiration_time("hrpws", "/hrp/v2/worker/"),
            FOUR_HOURS)
        self.assertEquals(
            cache.get_cache_expiration_time("bridge", "/api/author/users/"),
            FIVE_SECONDS)
        self.assertEquals(
            cache.get_cache_expiration_time(
                "bridge", "/api/author/custom_fields"),
            FIVE_MINS)
