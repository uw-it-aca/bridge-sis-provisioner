# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging
import time


def log_exception(logger, message, exc_info):
    """
    exc_info is a string containing the full stack trace,
    including the exception type and value
    """
    logger.error("{0} => {1}".format(message, exc_info.splitlines()))


def log_resp_time(logger, message, timer):
    logger.info("{0} Time={1} sec".format(message, timer.get_elapsed()))


class Timer:
    def __init__(self):
        """
        Start the timer
        """
        self.start = time.time()

    def get_elapsed(self):
        """
        Return the time spent in seconds
        """
        return time.time() - self.start
