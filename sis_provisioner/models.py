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


PRIORITY_NONE = 0
PRIORITY_NORMAL = 1
PRIORITY_HIGH = 2
PRIORITY_CHANGE_REGID = 3
PRIORITY_CHANGE_NETID = 4

PRIORITY_CHOICES = (
    (PRIORITY_NONE, 'none'),
    (PRIORITY_NORMAL, 'normal'),
    (PRIORITY_HIGH, 'high'),
    (PRIORITY_CHANGE_REGID, 'regid changed'),
    (PRIORITY_CHANGE_NETID, 'netid changed'),
)


class EmployeeAppointment(models.Model):
    app_number = models.PositiveSmallIntegerField()
    job_class_code = models.CharField(max_length=96)
    org_code = models.CharField(max_length=16)

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


class BridgeUser(models.Model):
    regid = models.CharField(max_length=32,
                             db_index=True,
                             unique=True)
    netid = models.SlugField(max_length=32,
                             db_index=True,
                             unique=True)
    last_visited_date = models.DateTimeField()
    import_priority = models.SmallIntegerField(default=1,
                                               choices=PRIORITY_CHOICES)
    terminate_date = models.DateTimeField(null=True)

    display_name = models.CharField(max_length=256, null=True)
    first_name = models.CharField(max_length=128, blank=True)
    last_name = models.CharField(max_length=128)
    email = models.CharField(max_length=64, null=True)
    is_alum = models.NullBooleanField()
    is_employee = models.NullBooleanField()
    is_faculty = models.NullBooleanField()
    is_staff = models.NullBooleanField()
    is_student = models.NullBooleanField()
    student_department1 = models.CharField(max_length=255, null=True)
    student_department2 = models.CharField(max_length=255, null=True)
    student_department3 = models.CharField(max_length=255, null=True)
    emp_appointments_data = models.TextField(max_length=2048, null=True)

    def __eq__(self, other):
        return other is not None and\
            self.regid == other.regid

    def is_stalled(self):
        # not validated for 15 days
        return self.last_visited_date + timedelta(days=15) < get_now()

    def save_verified(self):
        self.last_visited_date = get_now()
        self.set_no_action()
        self.terminate_date = None
        self.save()

    def no_action(self):
        return self.import_priority == PRIORITY_NONE

    def set_no_action(self):
        self.import_priority = PRIORITY_NONE

    def set_priority_normal(self):
        self.import_priority = PRIORITY_NORMAL

    def set_priority_netid_changed(self):
        self.import_priority = PRIORITY_CHANGE_NETID

    def set_priority_regid_changed(self):
        self.import_priority = PRIORITY_CHANGE_REGID

    def is_priority_normal(self):
        return self.import_priority == PRIORITY_NORMAL

    def is_priority_high(self):
        return self.import_priority == PRIORITY_HIGH

    def netid_changed(self):
        return self.import_priority == PRIORITY_CHANGE_NETID

    def regid_changed(self):
        return self.import_priority == PRIORITY_CHANGE_REGID

    def clear_terminate_date(self):
        if self.terminate_date:
            self.terminate_date = None
            self.save()

    def save_terminate_date(self, graceful=True):
        if graceful and self.terminate_date is not None:
            # not to change previously set date unless not graceful
            return
        self.terminate_date = get_now()
        if graceful:
            self.terminate_date += timedelta(days=15)
        self.save()

    def passed_terminate_date(self):
        return self.terminate_date is not None and\
            get_now() > self.terminate_date

    def has_display_name(self):
        return self.display_name is not None and\
            len(self.display_name) > 0 and\
            not self.display_name.isupper()

    def get_display_name(self, use_title=False):
        if self.has_display_name():
            return self.display_name

        if use_title:
            return "%s %s" % (self.first_name.title(),
                              self.last_name.title())

        name = HumanName("%s %s" % (self.first_name, self.last_name))
        name.capitalize()
        name.string_format = "{first} {last}"
        return str(name)

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
            "{%s: %s, %s: %s, %s: %s, %s: %s, %s: %s," +
            " %s: %s, %s: %s, %s: %s, %s: %s, %s: %s}") % (
            "netid", self.netid,
            "regid", self.regid,
            "last_visited_date", datetime_to_str(self.last_visited_date),
            "import_priority", self.import_priority,
            "terminate_date", datetime_to_str(self.terminate_date),
            "display_name", self.display_name,
            "first_name", self.first_name,
            "last_name", self.last_name,
            "email", self.email,
            "emp_appointments", self.emp_appointments_data)

    def json_data(self):
        return {
            "netid": self.netid,
            "regid": self.regid,
            "last_visited_date": datetime_to_str(self.last_visited_date),
            "import_priority": self.import_priority,
            "terminate_date": datetime_to_str(self.terminate_date),
            "display_name": self.display_name,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "emp_appointments": self.get_emp_appointments_json()
            }

    class Meta:
        db_table = 'uw_bridge_users'
