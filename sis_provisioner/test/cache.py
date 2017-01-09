from datetime import timedelta
from unittest2 import skipIf
from django.test import TestCase
from django.conf import settings
from restclients.mock_http import MockHTTP
from restclients.models import CacheEntryTimed
from restclients.exceptions import DataFailureException
from restclients.dao import SWS_DAO
from sis_provisioner.cache import BridgeAccountCache, get_cache_time
from sis_provisioner.test import user_file_name_override, fdao_gws_override,\
    fdao_pws_override


CACHE = 'sis_provisioner.cache.BridgeAccountCache'
ONE_HOUR = 60 * 60
FOUR_HOURS = 60 * 60 * 4
ONE_DAY = 60 * 60 * 24


@fdao_pws_override
@fdao_gws_override
@user_file_name_override
class TestCachePolicy(TestCase):

    def test_get_cache_time(self):
        self.assertEquals(get_cache_time("gws", "/group/"),
                          FOUR_HOURS)
        self.assertEquals(get_cache_time("pws", "/identity/v1/person/"),
                          FOUR_HOURS)
        self.assertEquals(get_cache_time("bridge", "/api/author/users/"),
                          ONE_HOUR)
        self.assertEquals(get_cache_time("bridge",
                                         "/api/author/custom_fields"),
                          ONE_DAY)

    def test_cache_expiration(self):
        with self.settings(RESTCLIENTS_DAO_CACHE_CLASS=CACHE):
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
                                      timedelta(minutes=(60 * 4) - 2))
            cache_entry.save()
            response = cache.getCache("gws", url, {})
            self.assertNotEquals(response, None)

            cache_entry.time_saved = (orig_time_saved -
                                      timedelta(minutes=(60 * 4) + 1))
            cache_entry.save()
            response = cache.getCache("gws", url, {})
            self.assertEquals(response, None)
