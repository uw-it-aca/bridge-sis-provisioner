from collections import defaultdict


def get_item_counts_dict(alist):
    counter = defaultdict(int)
    for item in alist:
        counter[item] += 1
    return counter
