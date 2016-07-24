from django.db import models
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

    hrp_home_dept_org_code = models.CharField(max_length=16, null=True)
    hrp_emp_status = models.CharField(max_length=2, null=True)
    # hrp_appointee = models.ForeignKey(Appointee, null=True)

    def __init__(self, *args, **kwargs):
        super(BridgeUser, self).__init__(*args, **kwargs)
        # self.hrp_appointee = None

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

    def __str__(self):
        return (
            "{%s: %s, %s: %s, %s: %s, %s: %s, %s: %s," +
            " %s: %s, %s: %s, %s: %s, %s: %s, %s: %s}") % (
            "netid", self.netid,
            "regid", self.regid,
            "last_visited_date", datetime_to_str(self.last_visited_date),
            "terminate_date", datetime_to_str(self.terminate_date),
            "display_name", self.display_name,
            "first_name", self.first_name,
            "last_name", self.last_name,
            "email", self.email,
            # "appointee", str(self.hrp_appointee)
            "hrp_home_dept_org_code", self.hrp_home_dept_org_code,
            "hrp_emp_status", self.hrp_emp_status,
            )

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
            "hrp_home_dept_org_code": self.hrp_home_dept_org_code,
            "hrp_emp_status": self.hrp_emp_status,
            }

    class Meta:
        db_table = 'uw_bridge_users'
