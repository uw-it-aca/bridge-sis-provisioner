import logging


logger = logging.getLogger(__name__)

CAMPUS = ["", "",
          "Seattle", "Seattle Health Sciences",
          "Seattle", "Bothell", "Tacoma"]

BASIC_HEADERS = ['UNIQUE ID', 'NAME', 'EMAIL', 'regid']
CHANGE_UID_HEADERS = ['prev uid', 'UNIQUE ID', 'NAME', 'EMAIL', 'regid']

EMP_HEADERS = ['emp campus 1', 'emp coll 1', 'emp dept 1',
               'emp campus 2', 'emp coll 2', 'emp dept 2',
               'emp campus 3', 'emp coll 3', 'emp dept 3']

STUD_HEADERS = ['student campus',
                'stud dept1', 'stud dept2', 'stud dept3'
                ]


def get_campus(emp_campus_code):
    try:
        return CAMPUS[int(emp_campus_code)]
    except Exception:
        return ""


def get_headers(changed_uid=False,
                include_hrp=False,
                include_student_dept=False):
    if changed_uid:
        retv = CHANGE_UID_HEADERS
    else:
        retv = BASIC_HEADERS
    if include_hrp:
        retv = retv + EMP_HEADERS

    if include_student_dept:
        retv = retv + STUD_HEADERS

    return retv


def get_attr_list(user,
                  changed_uid=False,
                  include_hrp=False,
                  include_student_dept=False):
    """
    Returns a list of data for creating a line of csv for a user
    matching the headers in header_for_users for the given UwBridgeUser object.
    """
    # The 1st item is the previous UID
    # The 2nd item is the uwEduEmailNameID attribute in IdP
    data = []
    if changed_uid:
        data.append(user.get_prev_bridge_uid())
    data = data + [
        user.get_bridge_uid(),
        user.get_display_name(),
        user.get_email(),
        user.regid]

    if include_hrp:
        data = data + get_emp_app_att_list(
            user.get_emp_appointments())

    if include_student_dept:
        pass

    return data


def get_campus_from_org_code(org_code):
    return get_campus(org_code[0:1])


def get_coll_from_org_code(org_code):
    return org_code[0:3]


def get_dept_from_org_code(org_code):
    return org_code[0:7]


def get_emp_app_att_list(emp_appointments):
    ret_alist = []
    i = 0
    while i < 3:
        if emp_appointments is not None and\
                i < len(emp_appointments):
            app = emp_appointments[i]
            ret_alist.append(get_campus_from_org_code(app.org_code))
            ret_alist.append(get_coll_from_org_code(app.org_code))
            ret_alist.append(get_dept_from_org_code(app.org_code))
        else:
            ret_alist = ret_alist + ["", "", ""]
        i += 1
    return ret_alist
