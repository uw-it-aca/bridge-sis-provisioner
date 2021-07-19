# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from collections import defaultdict


def get_item_counts_dict(alist):
    counter = defaultdict(int)
    for item in alist:
        counter[item] += 1
    return counter
