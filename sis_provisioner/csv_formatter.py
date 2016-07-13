import logging


logger = logging.getLogger(__name__)


def header_for_users():
    return ['Unique ID', 'Regid', 'Name', 'Email',
            'employee_department', 'student_department',
            'alumni', 'employee', 'faculty', 'staff', 'student']


def csv_for_user(user):
    """
    Returns a list of data for creating a line of csv for a user
    matching the headers in header_for_users for the given BridgeUser object.
    """
    uid = user.netid + "@washington.edu"

    if not user.email:
        email = "%s@uw.edu" % user.netid
    else:
        email = user.email

    if not user.student_department1:
        stud_dept = ""
    else:
        stud_dept = user.student_department1

    if not user.home_department:
        emp_dept = ""
    else:
        emp_dept = user.home_department

    return [uid, user.regid, user.get_fullname(), email,
            emp_dept, stud_dept,
            'y' if user.is_alum else 'n',
            'y' if user.is_employee else 'n',
            'y' if user.is_faculty else 'n',
            'y' if user.is_staff else 'n',
            'y' if user.is_student else 'n',
            ]
