from django.db import models
from datetime import timedelta
from django.utils import timezone
from nameparser import HumanName


def datetime_to_str(d_obj):
    if d_obj is not None:
        return d_obj.strftime("%Y-%m-%d %H:%M:%S")  # +00:00
    return None


def get_now():
    # return time-zone-aware datetime objects in UTC time.
    # Enable time zone support with USE_TZ=True in settings
    return timezone.now()


class BridgeUser(models.Model):
    regid = models.CharField(max_length=32,
                             db_index=True,
                             unique=True)
    netid = models.SlugField(max_length=32,
                             db_index=True,
                             unique=True)
    last_visited_date = models.DateTimeField()
    last_import_date = models.DateTimeField(null=True)
    last_import_err = models.CharField(max_length=10, null=True)
    terminate_date = models.DateTimeField(null=True)

    display_name = models.CharField(max_length=256, null=True)
    first_name = models.CharField(max_length=128, blank=True)
    last_name = models.CharField(max_length=128)
    email = models.CharField(max_length=64, null=True)
    home_department = models.CharField(max_length=255, null=True)
    student_department1 = models.CharField(max_length=255, null=True)
    student_department2 = models.CharField(max_length=255, null=True)
    student_department3 = models.CharField(max_length=255, null=True)
    is_alum = models.NullBooleanField()
    is_employee = models.NullBooleanField()
    is_faculty = models.NullBooleanField()
    is_staff = models.NullBooleanField()
    is_student = models.NullBooleanField()

    def __eq__(self, other):
        return other is not None and\
            self.regid == other.regid

    def has_netid_changed(self, uwnetid):
        return self.netid != uwnetid

    def to_import(self):
        # Return True if the user needs to be added into Bridge
        return self.last_import_date is None or\
            self.last_import_err is not None or\
            self.last_visited_date > self.last_import_date

    def to_be_purged(self):
        # Return True if the user is ready to be purged from Bridge
        return self.terminate_date is not None and\
            get_now() > self.terminate_date + timedelta(days=15)

    def get_fullname(self):
        # Generates the full name for a BridgeUser user.
        if self.display_name is not None and\
                len(self.display_name) > 0 and\
                not self.display_name.isupper():
            return self.display_name
        else:
            full_name = HumanName("%s %s" % (self.first_name, self.last_name))
            full_name.capitalize()
            full_name.string_format = "{last}, {first} {middle}"
            return str(full_name)

    def __str__(self):
        return (
            "{%s: %s, %s: %s, %s: %s, %s: %s, %s: %s, %s: %s, " +
            "%s: %s, %s: %s, %s: %s, %s: %s, %s: %s}") % (
            "netid", self.netid,
            "regid", self.regid,
            "last_visited_date", datetime_to_str(self.last_visited_date),
            "last_import_date", datetime_to_str(self.last_import_date),
            "last_import_err", self.last_import_err,
            "terminate_date", datetime_to_str(self.terminate_date),
            "display_name", self.display_name,
            "first_name", self.first_name,
            "last_name", self.last_name,
            "email", self.email
            )

    def json_data(self):
        return {
            "netid": self.netid,
            "regid": self.regid,
            "last_visited_date": datetime_to_str(self.last_visited_date),
            "last_import_date": datetime_to_str(self.last_import_date),
            "last_import_err": self.last_import_err,
            "terminate_date": datetime_to_str(self.terminate_date),
            "display_name": self.display_name,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email
            }

    class Meta:
        db_table = 'uw_bridge_users'
