import logging
import time


def log_exception(logger, message, exc_info):
    """
    exc_info is a string containing the full stack trace,
    including the exception type and value
    """
    logger.error("%s => %s",
                 message, exc_info.splitlines())


def log_resp_time(logger, message, timer):
    logger.info("%s Time=%f sec", message, timer.get_elapsed())


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
