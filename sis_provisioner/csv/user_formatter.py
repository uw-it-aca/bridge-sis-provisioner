import logging
from sis_provisioner.account_managers import (
    get_email, get_full_name, normalize_name,
    get_pos1_budget_code, get_pos1_job_code, get_job_title,
    get_pos1_job_class, get_pos1_org_code, get_pos1_org_name,
    get_supervisor_bridge_id)


logger = logging.getLogger(__name__)
BASIC_HEADERS = ['UNIQUE ID', 'email',
                 'full_name', 'first_name', 'last_name',
                 'regid', 'employee_id', 'student_id',
                 'job_title', 'manager_id', 'department',
                 'pos1_budget_code', 'pos1_job_code', 'pos1_job_class',
                 'pos1_org_code', 'pos1_org_name']


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
            get_pos1_budget_code(hrp_worker),
            get_pos1_job_code(hrp_worker),
            get_pos1_job_class(hrp_worker),
            get_pos1_org_code(hrp_worker),
            get_pos1_org_name(hrp_worker)]


def get_uid(netid):
    return "{}@uw.edu".format(netid)
