import logging


logger = logging.getLogger(__name__)
CAMPUS = ["", "",
          "Seattle", "Seattle Health Sciences",
          "Seattle", "Bothell", "Tacoma"]


def get_campus(emp_campus_code):
    if emp_campus_code:
        return CAMPUS[int(emp_campus_code)]
    return emp_campus_code


def get_headers(include_hrp=False,
                include_student_dept=False):
    headers = ['UNIQUE ID', 'NAME', 'EMAIL', 'regid',
               'alumni', 'employee', 'faculty', 'staff', 'student']
    if include_hrp:
        headers.append('emp home campus')

    if include_student_dept:
        headers.append('student dept name')

    return headers


def get_header_for_user_del():
    return ['UNIQUE ID']


def get_attr_list(user,
                  include_hrp=False,
                  include_student_dept=False):
    """
    Returns a list of data for creating a line of csv for a user
    matching the headers in header_for_users for the given BridgeUser object.
    """
    data = [user.netid + "@washington.edu",
            user.get_display_name(use_title=True),
            user.email if user.email else "%s@uw.edu" % user.netid,
            user.regid,
            'y' if user.is_alum else 'n',
            'y' if user.is_employee else 'n',
            'y' if user.is_faculty else 'n',
            'y' if user.is_staff else 'n',
            'y' if user.is_student else 'n',
            ]

    if include_hrp:
        emp_campus_code = 0
        if user.hrp_home_dept_org_code:
            emp_campus_code = user.hrp_home_dept_org_code[0:1]
        data.append(get_campus(emp_campus_code))

    if include_student_dept:
        student_dept_name = ""
        if user.student_department1:
            data.append(user.student_department1)

    return data
