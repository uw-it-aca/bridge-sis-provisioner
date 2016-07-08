import json
import logging
from restclients.util.log import log_err, log_info
from userservice.user import UserService


def log_exception(logger, message, exc_info):
    """
    exc_info is a string containing the full stack trace,
    including the exception type and value
    """
    logger.error("%s => %s",
                 message, exc_info.splitlines())


def log_invalid_netid_response(logger, timer):
    log_err(logger, 'Invalid netid, abort', timer)


def log_exception_with_timer(logger, timer, exc_info):
    log_err(logger, exc_info.splitlines(), timer)


def log_resp_time(logger, message, timer):
    log_info(logger, message, timer)
