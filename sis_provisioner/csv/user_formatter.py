import logging
from uw_bridge.models import BridgeCustomField
from sis_provisioner.account_managers import (
    get_email, get_full_name, normalize_name, get_job_title,
    get_pos_budget_code, get_pos_job_code, get_pos_location,
    get_pos_job_class, get_pos_org_code, get_pos_org_name,
    get_pos_unit_code, get_supervisor_bridge_id)
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
    # The 1st item is the previous UID
    # The 2nd item is the uwEduEmailNameID attribute in IdP
    return [get_uid(person.uwnetid),
            get_email(person),
            get_full_name(person),
            normalize_name(person.first_name),
            normalize_name(person.surname),
            person.uwregid,
            person.employee_id,
            person.student_number,
            get_job_title(hrp_worker),
            get_supervisor_bridge_id(hrp_worker),
            person.home_department,
            get_pos_budget_code(hrp_worker, 0),
            get_pos_job_code(hrp_worker, 0),
            get_pos_job_class(hrp_worker, 0),
            get_pos_location(hrp_worker, 0),
            get_pos_org_code(hrp_worker, 0),
            get_pos_org_name(hrp_worker, 0),
            get_pos_unit_code(hrp_worker, 0),
            get_pos_budget_code(hrp_worker, 1),
            get_pos_job_class(hrp_worker, 1),
            get_pos_job_code(hrp_worker, 1),
            get_pos_location(hrp_worker, 1),
            get_pos_org_code(hrp_worker, 1),
            get_pos_org_name(hrp_worker, 1),
            get_pos_unit_code(hrp_worker, 1)]


def get_uid(netid):
    return "{}@uw.edu".format(netid)
