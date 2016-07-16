import logging


logger = logging.getLogger(__name__)


def get_headers():
    return ['Unique ID', 'Regid', 'Name', 'Email',
            'alumni', 'employee', 'faculty', 'staff', 'student',
            'emp_status',
            'emp_home_dept_name',
            'emp_campus_code', 'emp_home_college_code', 'emp_home_dept_code',
            'student_dept_name',
            ]


def get_attr_list(user):
    """
    Returns a list of data for creating a line of csv for a user
    matching the headers in header_for_users for the given BridgeUser object.
    """
    uid = user.netid + "@washington.edu"

    if not user.email:
        email = "%s@uw.edu" % user.netid
    else:
        email = user.email

    student_dept_name = ""
    if user.student_department1:
        student_dept_name = user.student_department1

    emp_status = user.hrp_emp_status if user.hrp_emp_status else ""

    emp_home_dept_code = ""
    emp_campus_code = ""
    emp_home_college_code = ""
    if user.hrp_home_dept_org_code:
        emp_home_dept_code = user.hrp_home_dept_org_code
        emp_campus_code = emp_home_dept_code[0:1]
        emp_home_college_code = emp_home_dept_code[0:3]

    emp_home_dept_name = ""
    if user.hrp_home_dept_org_name:
        emp_home_dept_name = user.hrp_home_dept_org_name

    return [uid,
            user.regid,
            user.get_sortable_name(use_title=True),
            email,
            'y' if user.is_alum else 'n',
            'y' if user.is_employee else 'n',
            'y' if user.is_faculty else 'n',
            'y' if user.is_staff else 'n',
            'y' if user.is_student else 'n',
            emp_status,
            emp_home_dept_name,
            emp_campus_code,
            emp_home_college_code,
            emp_home_dept_code,
            student_dept_name,
            ]
