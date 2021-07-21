# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import json
from django.test import TestCase
from sis_provisioner.util.list_helper import get_item_counts_dict


class TestListHelper(TestCase):

    def test_get_item_counts(self):
        mylist = [2, 0, 1, 6, 7, 12, 0, 0, 1]
        counts = get_item_counts_dict(mylist)
        self.assertEqual(len(counts.keys()), 6)
        self.assertEqual(counts[0], 3)
        self.assertEqual(counts[1], 2)
        self.assertEqual(counts[2], 1)
        self.assertEqual(counts[6], 1)
        self.assertEqual(counts[7], 1)
        self.assertEqual(counts[12], 1)
        self.assertEqual(json.dumps(counts),
                         '{"2": 1, "0": 3, "1": 2, "6": 1, "7": 1, "12": 1}')
