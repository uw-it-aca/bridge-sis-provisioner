"""
This module encapsulates the interactions with the restclients.pws,
provides Person information of the current user
"""

import logging
from uw_pws import PWS
from restclients_core.exceptions import DataFailureException
from sis_provisioner.util.log import log_resp_time, Timer


logger = logging.getLogger(__name__)
pws = PWS()


def get_person(uwnetid):
    """
    Retrieve the Person object for the given netid
    Raise: DataFailureException
    """
    action = 'get_person_by_netid %s' % uwnetid
    timer = Timer()
    try:
        return pws.get_person_by_netid(uwnetid)
    finally:
        log_resp_time(logger, action, timer)


def get_person_by_regid(uwregid):
    """
    Retrieve the Person object for the given uwregid
    Raise: DataFailureException
    """
    action = 'get_person_by_regid %s' % uwregid
    timer = Timer()
    try:
        return pws.get_person_by_regid(uwregid)
    finally:
        log_resp_time(logger, action, timer)


def is_moved_netid(uwnetid):
    """
    Return True if the netid is Moved Permanently
    """
    try:
        person = pws.get_person_by_netid(uwnetid)
        return person.uwnetid != uwnetid
    except DataFailureException as ex:
        # if not follow redirect
        return (ex.status == 301)


def is_moved_regid(uwregid):
    """
    Return True if the regid is Moved Permanently
    """
    try:
        person = pws.get_person_by_regid(uwregid)
        return person.uwregid != uwregid
    except DataFailureException as ex:
        # if not follow redirect
        return (ex.status == 301)
