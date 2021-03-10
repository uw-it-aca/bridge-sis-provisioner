from datetime import timedelta
from django.test import TestCase
from django.conf import settings
from restclients_core.models import MockHTTP
from sis_provisioner.dao import DataFailureException
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
        self.assertEquals(cache.get_cache_expiration_time(
            "gws", "/group_sws/v3/group/"), ONE_HOUR)
        self.assertEquals(cache.get_cache_expiration_time(
            "pws", "/identity/v2/person/"), FOUR_HOURS)
        self.assertEquals(cache.get_cache_expiration_time(
            "hrpws", "/hrp/v2/worker/"), FOUR_HOURS)
        self.assertEquals(cache.get_cache_expiration_time(
            "bridge", "/api/author/users/"), FIVE_SECONDS)
        self.assertEquals(cache.get_cache_expiration_time(
            "bridge", "/api/author/custom_fields"), FIVE_MINS)

    def skip_test_cache_expiration(self):
        cache = BridgeAccountCache()
        ok_response = MockHTTP()
        ok_response.status = 200
        ok_response.data = "xx"
        url = '/group/uw_member/effective_member'

        response = cache.getCache('gws', url, {})
        self.assertEquals(response, None)

        cache.processResponse("gws", url, ok_response)
        response = cache.getCache("gws", url, {})
        self.assertEquals(response["response"].data, 'xx')

        cache_entry = CacheEntryTimed.objects.get(service='gws', url=url)
        orig_time_saved = cache_entry.time_saved
        cache_entry.time_saved = (orig_time_saved -
                                  timedelta(minutes=(60) - 2))
        cache_entry.save()
        response = cache.getCache("gws", url, {})
        self.assertNotEquals(response, None)

        cache_entry.time_saved = (orig_time_saved -
                                  timedelta(minutes=(60) + 1))
        cache_entry.save()
        response = cache.getCache("gws", url, {})
        self.assertEquals(response, None)
