# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import fnmatch
import os
from django.test import TestCase
from sis_provisioner.dao import (
    DataFailureException, read_gws_cache_file, write_gws_cache_file)
from sis_provisioner.dao.gws import (
    get_members_of_group, get_potential_users, get_bridge_authors,
    get_member_updates)
from sis_provisioner.tests import fdao_gws_override


@fdao_gws_override
class TestGwsDao(TestCase):

    def test_get_affiliate(self):
        self.assertRaises(DataFailureException, get_members_of_group, "uw")

    def test_get_potential_users(self):
        user_set = get_potential_users()
        self.assertEqual(len(user_set), 7)
        self.assertTrue("retiree" in user_set)
        self.assertTrue("affiemp" in user_set)
        self.assertTrue("faculty" in user_set)
        self.assertTrue("javerage" in user_set)
        self.assertTrue("not_in_pws" in user_set)
        self.assertTrue("error500" in user_set)
        self.assertTrue("staff" in user_set)

    def test_get_bridge_authors(self):
        user_set = get_bridge_authors()
        self.assertEqual(len(user_set), 5)
        self.assertTrue("alumni" in user_set)
        self.assertTrue("javerage" in user_set)
        self.assertTrue("staff" in user_set)
        self.assertTrue("error500" in user_set)
        self.assertTrue("not_in_pws" in user_set)

    def test_gws_cache_file(self):
        with self.settings(BRIDGE_GWS_CACHE='/tmp/gwsusers'):
            current_user_set = get_potential_users()
            netids = get_member_updates(current_user_set)
            self.assertEqual(len(netids), 7)

            # test file read
            cache = read_gws_cache_file('/tmp/gwsusers')
            self.assertEqual(cache, netids)

            # test file rename
            write_gws_cache_file('/tmp/gwsusers', current_user_set)
            files = fnmatch.filter(os.listdir('/tmp/'), 'gwsuser*')
            self.assertEqual(len(files), 2)
