# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from datetime import timedelta
import logging
from restclients_core.exceptions import (
    DataFailureException, InvalidNetID, InvalidRegID)
from uw_gws import GWS_DAO
from sis_provisioner.models import get_now


logger = logging.getLogger(__name__)


def get_dt_from_now(duration):
    return get_now() - timedelta(minutes=duration)


def changed_since_str(duration, iso=False):
    if iso:
        return get_dt_from_now(duration).strftime('%Y-%m-%dT%H:%M:%S.%f%z')
    return get_dt_from_now(duration).strftime("%Y-%m-%d %H:%M:%S")


def is_using_file_dao():
    return GWS_DAO().get_implementation().is_mock()
