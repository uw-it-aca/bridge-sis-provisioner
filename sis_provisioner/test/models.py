from django.test import TransactionTestCase
from datetime import timedelta, datetime
from sis_provisioner.models import UwBridgeUser, EmployeeAppointment,\
    get_now, datetime_to_str
from sis_provisioner.test import fdao_pws_override
from sis_provisioner.test.dao import mock_uw_bridge_user


@fdao_pws_override
class TestModels(TransactionTestCase):

    def test_save_terminate(self):
        user, person = mock_uw_bridge_user('staff')
        self.assertIsNone(user.terminate_at)
        user.save_terminate_date()
        self.assertFalse(user.passed_terminate_date())

        user.terminate_at -= timedelta(days=16)
        self.assertTrue(user.passed_terminate_date())

        user.save_terminate_date(graceful=False)
        dtime = user.terminate_at
        self.assertTrue(get_now() < (dtime + timedelta(seconds=3)))

        user.clear_terminate_date()
        self.assertIsNone(user.terminate_at)

    def test_last_visited(self):
        user, person = mock_uw_bridge_user('staff')
        self.assertFalse(user.is_stalled())
        user.last_visited_at =\
            user.last_visited_at - timedelta(days=16)
        self.assertTrue(user.is_stalled())
        user.save_verified()
        self.assertTrue(
            get_now() < (user.last_visited_at + timedelta(seconds=3)))

    def test_action_mothods(self):
        user, person = mock_uw_bridge_user('staff')
        self.assertTrue(user.no_action())

        user.set_action_new()
        self.assertFalse(user.no_action())
        self.assertTrue(user.is_new())
        self.assertFalse(user.netid_changed())
        self.assertFalse(user.regid_changed())
        self.assertFalse(user.is_update())

        user.set_action_restore()
        self.assertFalse(user.no_action())
        self.assertTrue(user.is_restore())
        self.assertFalse(user.netid_changed())
        self.assertFalse(user.regid_changed())
        self.assertFalse(user.is_new())
        self.assertFalse(user.is_update())

        user.prev_netid = "ppp"
        user.set_action_update()
        self.assertFalse(user.is_new())
        self.assertTrue(user.netid_changed())
        self.assertFalse(user.regid_changed())
        self.assertTrue(user.is_update())

        user.disable()
        self.assertTrue(user.disabled)
        user.save_terminate_date(graceful=False)
        user.save_verified()
        self.assertFalse(user.disabled)
        self.assertIsNone(user.terminate_at)
        self.assertIsNone(user.prev_netid)

        user.set_action_regid_changed()
        self.assertFalse(user.is_new())
        self.assertFalse(user.netid_changed())
        self.assertTrue(user.regid_changed())
        self.assertFalse(user.is_update())

    def test_set_bridge_id(self):
        user, person = mock_uw_bridge_user('staff')
        self.assertEqual(user.bridge_id, 0)
        user.set_bridge_id(123)
        self.assertEqual(user.bridge_id, 123)

    def test_display_name(self):
        user, person = mock_uw_bridge_user('staff')
        self.assertTrue(user.has_display_name())

    def test_emp_appointments(self):
        emp_app = EmployeeAppointment()
        emp_app.load_from_json({"an": 2, "jc": "0191", "oc": "2540574070"})
        self.assertEqual(emp_app.app_number, 2)
        self.assertEqual(emp_app.job_class_code, "0191")
        self.assertEqual(emp_app.org_code, "2540574070")
        self.assertEqual(emp_app.json_dump_compact(),
                         '{"an":2,"jc":"0191","oc":"2540574070"}')
        self.assertEqual(emp_app.to_json(),
                         {"an": 2,
                          "jc": "0191",
                          "oc": "2540574070"})

    def test_datetime_to_str(self):
        dt = datetime(2017, 12, 5, 15, 3, 1)
        self.assertEqual(datetime_to_str(dt), "2017-12-05 15:03:01")
        self.assertIsNone(datetime_to_str(None))
