from django.db import models
import json
from datetime import timedelta
from django.utils import timezone
from nameparser import HumanName
# from restclients.models.hrp import Appointee


def datetime_to_str(d_obj):
    if d_obj is not None:
        return d_obj.strftime("%Y-%m-%d %H:%M:%S")  # +00:00
    return None


def get_now():
    # return time-zone-aware datetime objects in UTC time.
    # Enable time zone support with USE_TZ=True in settings
    return timezone.now()


class EmployeeAppointment(models.Model):
    app_number = models.PositiveSmallIntegerField()
    job_class_code = models.CharField(max_length=96)
    org_code = models.CharField(max_length=16)

    def __init__(self, *args, **kwargs):
        super(EmployeeAppointment, self).__init__(*args, **kwargs)

    def __cmp__(self, other):
        if other is not None:
            return self.app_number.__cmp__(other.app_number)

    def __eq__(self, other):
        return self.app_number == other.app_number and\
            self.job_class_code == other.job_class_code and\
            self.org_code == other.org_code

    def __lt__(self, other):
        return self.app_number < other.app_number

    def to_json(self):
        return {
            'an': self.app_number,
            'jc': self.job_class_code,
            'oc': self.org_code,
            }

    def json_dump_compact(self):
        return json.dumps(self.to_json(),
                          separators=(',', ':'),
                          sort_keys=True)

    def load_from_json(self, json_data):
        if json_data:
            self.app_number = json_data.get("an")
            self.job_class_code = json_data.get("jc")
            self.org_code = json_data.get("oc")
        return self

    def __str__(self):
        return ("{%s: %s, %s: %s, %s: %s}" % (
                'app_number', self.app_number,
                'job_class_code', self.job_class_code,
                'org_code', self.org_code))


ACTION_NONE = 0
ACTION_NEW = 1
ACTION_UPDATE = 2
ACTION_CHANGE_REGID = 3
ACTION_RESTORE = 4
ACTION_CHOICES = (
    (ACTION_NONE, 'none'),
    (ACTION_NEW, 'add new'),
    (ACTION_UPDATE, 'update'),
    (ACTION_CHANGE_REGID, 'change regid'),
    (ACTION_RESTORE, 'restore'),
    )


class UwBridgeUser(models.Model):
    regid = models.CharField(max_length=32,
                             primary_key=True)
    bridge_id = models.IntegerField(default=0)
    netid = models.SlugField(max_length=32,
                             db_index=True,
                             unique=True)
    prev_netid = models.SlugField(max_length=32,
                                  null=True,
                                  default=None)
    action_priority = models.SmallIntegerField(default=ACTION_NONE,
                                               choices=ACTION_CHOICES)
    disabled = models.NullBooleanField(default=False)
    last_visited_at = models.DateTimeField()
    terminate_at = models.DateTimeField(null=True,
                                        default=None)
    display_name = models.CharField(max_length=256,
                                    null=True,
                                    default=None)
    first_name = models.CharField(max_length=128,
                                  null=True,
                                  default=None)
    last_name = models.CharField(max_length=128)
    email = models.CharField(max_length=128,
                             null=True,
                             default=None)
    is_alum = models.NullBooleanField(default=False)
    is_employee = models.NullBooleanField(default=False)
    is_faculty = models.NullBooleanField(default=False)
    is_staff = models.NullBooleanField(default=False)
    is_student = models.NullBooleanField(default=False)
    emp_appointments_data = models.TextField(max_length=2048,
                                             null=True, blank=True,
                                             default=None)

    def __init__(self, *args, **kwargs):
        super(UwBridgeUser, self).__init__(*args, **kwargs)

    def __eq__(self, other):
        return other is not None and\
            self.regid == other.regid and\
            self.netid == other.netid and\
            self.first_name == other.first_name and\
            self.last_name == other.last_name and\
            self.email == other.email and\
            self.is_alum == other.is_alum and\
            self.is_employee == other.is_employee and\
            self.is_faculty == other.is_faculty and\
            self.is_staff == other.is_staff and\
            self.is_student == other.is_student and\
            self.emp_appointments_data == other.emp_appointments_data

    def is_stalled(self):
        # not validated for 15 days
        return self.last_visited_at + timedelta(days=15) < get_now()

    def save_verified(self):
        self.last_visited_at = get_now()
        self.set_no_action()
        self.disabled = False
        self.prev_netid = None
        self.terminate_at = None
        self.save()

    def set_bridge_id(self, bridge_id):
        if bridge_id:
            self.bridge_id = bridge_id
            self.save()

    def no_action(self):
        return self.action_priority == ACTION_NONE

    def set_no_action(self):
        self.action_priority = ACTION_NONE

    def set_action_new(self):
        self.action_priority = ACTION_NEW

    def set_action_update(self):
        self.action_priority = ACTION_UPDATE

    def set_action_regid_changed(self):
        self.action_priority = ACTION_CHANGE_REGID

    def set_action_restore(self):
        self.action_priority = ACTION_RESTORE

    def is_new(self):
        return self.action_priority == ACTION_NEW

    def is_restore(self):
        return self.action_priority == ACTION_RESTORE

    def is_update(self):
        return self.action_priority == ACTION_UPDATE

    def netid_changed(self):
        return self.prev_netid is not None

    def regid_changed(self):
        return self.action_priority == ACTION_CHANGE_REGID

    def clear_terminate_date(self):
        if self.terminate_at:
            self.terminate_at = None
            self.save()

    def disable(self):
        self.disabled = True
        self.save()

    def save_terminate_date(self, graceful=True):
        if graceful and self.terminate_at is not None:
            # not to change previously set date unless not graceful
            return
        self.terminate_at = get_now()
        if graceful:
            self.terminate_at += timedelta(days=15)
        self.save()

    def passed_terminate_date(self):
        return self.terminate_at is not None and\
            get_now() > self.terminate_at

    def has_display_name(self):
        return self.display_name is not None and\
            len(self.display_name) > 0 and\
            not self.display_name.isupper()

    def get_display_name(self):
        if self.has_display_name():
            return self.display_name
        if self.first_name is not None:
            name = HumanName("%s %s" % (self.first_name, self.last_name))
        else:
            name = HumanName(self.last_name)

        name.capitalize()
        name.string_format = "{first} {last}"
        return str(name)

    def get_email(self):
        if self.email:
            return self.email
        return "%s@uw.edu" % self.netid

    def has_emp_appointments(self):
        return self.emp_appointments_data is not None and\
            len(self.emp_appointments_data) > 2

    def get_emp_appointments_json(self):
        if self.has_emp_appointments():
            return json.loads(self.emp_appointments_data)
        return None

    def get_total_emp_apps(self):
        if self.has_emp_appointments():
            return len(self.get_emp_appointments_json())
        return 0

    def get_emp_appointments(self):
        emp_apps = []
        json_data = self.get_emp_appointments_json()
        if json_data is not None:
            i = 0
            while i < len(json_data):
                emp_apps.append(
                    EmployeeAppointment().load_from_json(json_data[i]))
                i += 1
        return emp_apps

    def __str__(self):
        return (
            "{%s: %s, %s: %s, %s: %s, %s: %s, %s: %s, %s: %s," +
            " %s: %s, %s: %s, %s: %s, %s: %s, %s: %s, %s: %s}") % (
            "netid", self.netid,
            "prev_netid", self.prev_netid,
            "regid", self.regid,
            "last_visited_at", datetime_to_str(self.last_visited_at),
            "action_priority", self.get_action_priority_display(),
            "disabled", self.disabled,
            "terminate_at", datetime_to_str(self.terminate_at),
            "display_name", self.get_display_name(),
            "first_name", self.first_name,
            "last_name", self.last_name,
            "email", self.get_email(),
            "emp_appointments", self.emp_appointments_data)

    def json_data(self):
        return {
            "netid": self.netid,
            "regid": self.regid,
            "prev_netid": self.prev_netid,
            "last_visited_at": datetime_to_str(self.last_visited_at),
            "terminate_at": datetime_to_str(self.terminate_at),
            "display_name": self.get_display_name(),
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.get_email(),
            "emp_appointments": self.get_emp_appointments_json()
            }

    class Meta:
        db_table = 'uw_bridge_users'
