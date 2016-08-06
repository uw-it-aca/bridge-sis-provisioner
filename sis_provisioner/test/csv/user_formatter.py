from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings
from sis_provisioner.csv.user_formatter import get_headers, get_attr_list,\
    get_header_for_user_del, get_campus, get_emp_app_att_list,\
    get_campus_from_org_code, get_coll_from_org_code,\
    get_dept_from_org_code
from sis_provisioner.models import EmployeeAppointment, BridgeUser, get_now


class TestUserFormatter(TestCase):

    def test_get_campus(self):
        self.assertEqual(get_campus(None), "")
        self.assertEqual(get_campus(1), "")
        self.assertEqual(get_campus(2), "Seattle")
        self.assertEqual(get_campus(3), "Seattle Health Sciences")
        self.assertEqual(get_campus(4), "Seattle")
        self.assertEqual(get_campus(5), "Bothell")
        self.assertEqual(get_campus(6), "Tacoma")
        self.assertEqual(get_campus(7), "")

    def test_get_campus_from_org_code(self):
        self.assertEqual(get_campus_from_org_code("2000000000"), "Seattle")
        self.assertEqual(get_campus_from_org_code("3000000000"),
                         "Seattle Health Sciences")
        self.assertEqual(get_campus_from_org_code("4000000000"), "Seattle")
        self.assertEqual(get_campus_from_org_code("5000000000"), "Bothell")
        self.assertEqual(get_campus_from_org_code("6000000000"), "Tacoma")

    def test_get_coll_from_org_code(self):
        self.assertEqual(get_coll_from_org_code("2000000000"), "200")

    def test_get_dept_from_org_code(self):
        self.assertEqual(get_dept_from_org_code("2000000000"), "2000000")

    def test_get_headers_for_user_del(self):
        self.assertEqual(len(get_header_for_user_del()), 1)
        self.assertEqual(','.join(get_header_for_user_del()),
                         ("UNIQUE ID"))

    def test_get_emp_app_att_list(self):
        self.assertEqual(','.join(get_emp_app_att_list([])),
                         ',,,,,,,,')
        apps = []
        apps.append(EmployeeAppointment(app_number=1,
                                        job_class_code="0",
                                        org_code="5200005000"))
        apps.append(EmployeeAppointment(app_number=2,
                                        job_class_code="0",
                                        org_code="5100001000"))
        emp_attrs = get_emp_app_att_list(apps)
        self.assertEqual(len(emp_attrs), 9)
        self.assertEqual(emp_attrs[0], "Bothell")
        self.assertEqual(emp_attrs[1], "520")
        self.assertEqual(emp_attrs[2], "5200005")
        self.assertEqual(emp_attrs[3], "Bothell")
        self.assertEqual(emp_attrs[4], "510")
        self.assertEqual(emp_attrs[5], "5100001")
        self.assertEqual(emp_attrs[6], "")
        self.assertEqual(emp_attrs[7], "")
        self.assertEqual(emp_attrs[8], "")

    def test_get_headers(self):
        headers1 = get_headers()
        self.assertEqual(len(headers1), 4)
        self.assertEqual(','.join(headers1),
                         ("UNIQUE ID,NAME,EMAIL,regid"))
        headers = get_headers(include_hrp=True)
        self.assertEqual(len(headers), 13)
        self.assertEqual(','.join(headers),
                         ("UNIQUE ID,NAME,EMAIL,regid," +
                          "emp campus 1,emp coll 1,emp dept 1," +
                          "emp campus 2,emp coll 2,emp dept 2," +
                          "emp campus 3,emp coll 3,emp dept 3"
                          ))

    def test_get_attr_list_withhrp(self):
        user = BridgeUser(netid='staff',
                          regid="10000000000000000000000000000001",
                          last_visited_date=get_now(),
                          display_name="James Staff",
                          last_name="Staf",
                          emp_appointments_data=None)
        user_attr_list = get_attr_list(user, include_hrp=True)
        self.assertEqual(len(user_attr_list), 13)
        self.assertEqual(user_attr_list[0],
                         "staff@uw.edu")
        self.assertEqual(user_attr_list[1],
                         "James Staff")
        self.assertEqual(user_attr_list[2],
                         "staff@uw.edu")
        self.assertEqual(user_attr_list[3],
                         "10000000000000000000000000000001")
        self.assertEqual(user_attr_list[4], "")

        apps_data = '[{"an":2,"jc":"0191","oc":"2540574070"}]'
        user = BridgeUser(netid='faculty',
                          regid="10000000000000000000000000000005",
                          last_visited_date=get_now(),
                          first_name="James",
                          last_name="Faculty",
                          emp_appointments_data=apps_data)
        self.assertEqual(user.emp_appointments_data, apps_data)
        self.assertEqual(user.get_total_emp_apps(), 1)
        user_attr_list = get_attr_list(user, include_hrp=True)
        self.assertEqual(len(user_attr_list), 13)
        self.assertEqual(user_attr_list[0],
                         "faculty@uw.edu")
        self.assertEqual(user_attr_list[1],
                         "James Faculty")
        self.assertEqual(user_attr_list[2],
                         "faculty@uw.edu")
        self.assertEqual(user_attr_list[3],
                         "10000000000000000000000000000005")
        self.assertEqual(user_attr_list[4], "Seattle")

        apps_data = '[{"an":2,"jc":"0875","oc":"5100001000"}]'
        user = BridgeUser(netid='botgrad',
                          regid="10000000000000000000000000000002",
                          last_visited_date=get_now(),
                          first_name="Bothell Graduate",
                          last_name="student",
                          emp_appointments_data=apps_data)
        user_attr_list = get_attr_list(user, include_hrp=True)
        self.assertEqual(len(user_attr_list), 13)
        self.assertEqual(user_attr_list[0],
                         "botgrad@uw.edu")
        self.assertEqual(user_attr_list[4], "Bothell")

        apps_data = '[{"an":2,"jc":"0875","oc":"6100002000"}]'
        user = BridgeUser(netid='tacgrad',
                          regid="10000000000000000000000000000004",
                          last_visited_date=get_now(),
                          first_name="Tacoma Graduate",
                          last_name="student",
                          emp_appointments_data=apps_data)
        user_attr_list = get_attr_list(user, include_hrp=True)
        self.assertEqual(len(user_attr_list), 13)
        self.assertEqual(user_attr_list[0],
                         "tacgrad@uw.edu")
        self.assertEqual(user_attr_list[4], "Tacoma")

        user = BridgeUser(netid='retiree',
                          regid="10000000000000000000000000000006",
                          last_visited_date=get_now(),
                          first_name="Ellen Louise",
                          last_name="Retiree")
        user_attr_list = get_attr_list(user, include_hrp=True)
        self.assertEqual(len(user_attr_list), 13)
        self.assertEqual(user_attr_list[1], "Ellen Retiree")
        self.assertEqual(user_attr_list[4], "")

    def test_get_attr_list_nohrp(self):
        user = BridgeUser(netid='staff',
                          regid="10000000000000000000000000000001",
                          last_visited_date=get_now(),
                          display_name="James Staff",
                          last_name="Staf")
        user_attr_list = get_attr_list(user)
        self.assertEqual(len(user_attr_list), 4)
        self.assertEqual(user_attr_list[0],
                         "staff@uw.edu")

        user = BridgeUser(netid='faculty',
                          regid="10000000000000000000000000000005",
                          last_visited_date=get_now(),
                          first_name="James",
                          last_name="Faculty")
        user_attr_list = get_attr_list(user)
        self.assertEqual(len(user_attr_list), 4)
        self.assertEqual(user_attr_list[0],
                         "faculty@uw.edu")
        self.assertEqual(user_attr_list[1],
                         "James Faculty")
        self.assertEqual(user_attr_list[2],
                         "faculty@uw.edu")
        self.assertEqual(user_attr_list[3],
                         "10000000000000000000000000000005")
