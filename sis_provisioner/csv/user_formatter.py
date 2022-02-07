# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging
from uw_bridge.models import BridgeCustomField
from sis_provisioner.account_managers import (
    get_email, get_full_name, normalize_name, get_job_title,
    GET_POS_ATT_FUNCS, get_supervisor_bridge_id)
from sis_provisioner.models.work_positions import WORK_POSITION_FIELDS
from sis_provisioner.util.settings import get_total_work_positions_to_load


logger = logging.getLogger(__name__)


def get_headers():
    headers = ['UNIQUE ID', 'email', 'full_name', 'first_name', 'last_name',
               BridgeCustomField.REGID_NAME,
               BridgeCustomField.EMPLOYEE_ID_NAME,
               BridgeCustomField.STUDENT_ID_NAME,
               'job_title', 'manager_id', 'department']
    for pos_num in range(get_total_work_positions_to_load()):
        pos_field_names = WORK_POSITION_FIELDS[pos_num]
        for i in range(len(pos_field_names)):
            headers.append(pos_field_names[i])
    return headers


def get_attr_list(person, hrp_worker):
    """
    Returns a list of data for creating a line of csv for a user
    matching the headers
    """
    row = [get_uid(person.uwnetid),
           get_email(person),
           get_full_name(person),
           normalize_name(person.first_name),
           normalize_name(person.surname),
           person.uwregid,
           person.employee_id,
           person.student_number,
           get_job_title(hrp_worker),
           get_supervisor_bridge_id(hrp_worker),
           person.home_department]
    for pos_num in range(get_total_work_positions_to_load()):
        for i in range(len(GET_POS_ATT_FUNCS)):
            row.append(GET_POS_ATT_FUNCS[i](hrp_worker, pos_num))
    return row


def get_uid(netid):
    return "{}@uw.edu".format(netid)
