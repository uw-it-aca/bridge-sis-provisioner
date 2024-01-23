# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging
import re
from string import capwords
from nameparser import HumanName
from uw_bridge.models import BridgeCustomField
from sis_provisioner.dao.uw_account import get_by_employee_id


logger = logging.getLogger(__name__)


def get_email(person):
    email = None
    for email_address in person.email_addresses:
        if "@uw.edu" in email_address:
            email = re.sub(" ", "", email_address)
            break
    if not email or len(email) == 0:
        return "{0}@uw.edu".format(person.uwnetid)
    return re.sub(r"\.$", "", email, flags=re.IGNORECASE)


def get_first_name(person):
    return (
        person.preferred_first_name
        if person.preferred_first_name and len(person.preferred_first_name)
        else person.first_name)


def get_full_name(person):
    if (len(person.display_name) > 0 and
            not person.display_name.isdigit() and
            not person.display_name.isupper()):
        return person.display_name

    name = HumanName(person.full_name)
    name.capitalize()
    name.string_format = "{first} {last}"
    return str(name)


def get_surname(person):
    return (
        person.preferred_surname
        if person.preferred_surname and len(person.preferred_surname)
        else person.surname)


def normalize_name(name):
    """
    Return a title faced name if the name is not empty
    """
    if name is not None and len(name) > 0:
        return capwords(name)
    return ""


def get_custom_field_value(bridge_account, field_name):
    cf = bridge_account.get_custom_field(field_name)
    if cf is not None:
        return cf.value
    return ""


def get_work_position(hrp_wkr, position_num):
    """
    :param position_num: [0..get_total_work_positions_to_load-1]
    """
    if hrp_wkr and len(hrp_wkr.worker_details):
        positions = hrp_wkr.worker_details[0]
        if position_num == 0:
            return positions.primary_position
        if position_num >= 1:
            index = position_num - 1
            if len(positions.other_active_positions) > index:
                return positions.other_active_positions[index]
    return None


def get_job_title(hrp_wkr):
    pos = get_work_position(hrp_wkr, 0)
    return pos.job_title if pos else None


def get_pos_job_class(hrp_wkr, position_num):
    pos = get_work_position(hrp_wkr, position_num)
    return pos.job_class if pos else None


def get_pos_location(hrp_wkr, position_num):
    pos = get_work_position(hrp_wkr, position_num)
    return pos.location if pos else None


def get_pos_job_code(hrp_wkr, position_num):
    pos = get_work_position(hrp_wkr, position_num)
    if pos is not None and pos.job_profile is not None:
        return pos.job_profile.job_code
    return None


def get_pos_hr_org(hrp_wkr, position_num):
    pos = get_work_position(hrp_wkr, position_num)
    return pos.hr_org if pos else None


def get_pos_org_code(hrp_wkr, position_num):
    pos = get_work_position(hrp_wkr, position_num)
    return pos.org_code if pos else None


def get_pos_org_name(hrp_wkr, position_num):
    pos = get_work_position(hrp_wkr, position_num)
    return pos.org_name if pos else None


def get_pos_unit_code(hrp_wkr, position_num):
    pos = get_work_position(hrp_wkr, position_num)
    return pos.org_unit_code if pos else None


# make sure the order is consistent with that in
# sis_provisioner.models.work_positions.WORK_POSITION_FIELDS
GET_POS_ATT_FUNCS = [get_pos_hr_org, get_pos_job_class, get_pos_job_code,
                     get_pos_location, get_pos_org_code, get_pos_org_name,
                     get_pos_unit_code]


def get_supervisor_bridge_id(hrp_wkr):
    if hrp_wkr is not None:
        manager_employee_id = hrp_wkr.primary_manager_id
        if manager_employee_id is None:
            return 0
        if manager_employee_id == hrp_wkr.employee_id:
            logger.error("Managere EID==own EID: {0}".format(hrp_wkr))
            return 0
        uw_acc = get_by_employee_id(manager_employee_id)
        if (uw_acc is not None and uw_acc.netid != hrp_wkr.netid):
            return uw_acc.bridge_id
    return 0
