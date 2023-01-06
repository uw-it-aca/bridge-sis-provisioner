# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import json
from django.db import models
from datetime import datetime, timedelta
from pytz import timezone

GRACE_PERIOD = 180


def datetime_to_str(dt):
    return (
        dt.isoformat() if dt is not None and isinstance(dt, datetime)
        else None)


def get_now():
    # return time-zone-aware datetime object
    return datetime.now(timezone("US/Pacific"))


class UwAccount(models.Model):
    netid = models.SlugField(max_length=50, db_index=True, unique=True)
    prev_netid = models.SlugField(max_length=50, null=True, default=None)
    bridge_id = models.IntegerField(default=0, db_index=True)
    employee_id = models.SlugField(max_length=10, null=True,
                                   default=None, db_index=True)
    disabled = models.BooleanField(default=False)
    last_updated = models.DateTimeField(null=True, default=None)
    # scheduled terminate date
    terminate_at = models.DateTimeField(null=True, default=None)

    def has_bridge_id(self):
        return self.bridge_id > 0

    def set_bridge_id(self, bridge_id):
        self.bridge_id = bridge_id

    def has_employee_id(self):
        return self.employee_id is not None

    def set_employee_id(self, employee_id):
        if self.has_employee_id() or employee_id != self.employee_id:
            self.employee_id = employee_id
            self.save()

    def set_ids(self, bridge_id, employee_id):
        upded = False
        if bridge_id > 0 and bridge_id != self.bridge_id:
            self.set_bridge_id(bridge_id)
            upded = True

        if (employee_id is not None and
                self.has_employee_id() or employee_id != self.employee_id):
            self.employee_id = employee_id
            upded = True

        if upded:
            self.last_updated = get_now()
            self.save()

    def has_prev_netid(self):
        return self.prev_netid is not None and len(self.prev_netid) > 0

    def netid_changed(self):
        return self.has_prev_netid()

    def set_disable(self):
        self.disabled = True
        self.last_updated = get_now()
        self.save()

    def set_restored(self):
        self.disabled = False
        self.terminate_at = None
        self.last_updated = get_now()
        self.save()

    def has_terminate_date(self):
        return self.terminate_at is not None

    def set_terminate_date(self, graceful=True):
        # not to change previously set date unless not graceful
        if graceful and self.has_terminate_date():
            return
        self.terminate_at = get_now()
        if graceful:
            self.terminate_at += timedelta(days=GRACE_PERIOD)
        self.last_updated = get_now()
        self.save()

    def passed_terminate_date(self):
        return self.has_terminate_date() and\
            get_now() > self.terminate_at

    def set_updated(self):
        self.disabled = False
        self.prev_netid = None
        self.terminate_at = None
        self.last_updated = get_now()
        self.save()

    def json_data(self):
        return {
            "netid": self.netid,
            "bridge_id": self.bridge_id,
            'employee_id': self.employee_id,
            "prev_netid": self.prev_netid,
            "disabled": self.disabled,
            "last_updated": datetime_to_str(self.last_updated),
            "terminate_at": datetime_to_str(self.terminate_at),
            }

    def __init__(self, *args, **kwargs):
        super(UwAccount, self).__init__(*args, **kwargs)

    def __eq__(self, other):
        return (self.netid == other.netid and
                (self.prev_netid is None and other.prev_netid is None or
                 self.prev_netid == other.prev_netid))

    def __hash__(self):
        return super().__hash__()

    def __str__(self):
        return json.dumps(self.json_data(), default=str)

    class Meta:
        db_table = 'uwuseraccounts'
        app_label = 'sis_provisioner'

    @classmethod
    def exists(cls, uwnetid):
        return UwAccount.objects.filter(netid=uwnetid).exists()

    @classmethod
    def get(cls, uwnetid):
        return UwAccount.objects.get(netid=uwnetid)

    @classmethod
    def get_uw_acc(cls, cur_uwnetid, prior_uwnetids, create=False):
        if UwAccount.exists(cur_uwnetid):
            return UwAccount.get(cur_uwnetid)

        # no entry for the current netid
        for prior_netid in prior_uwnetids:
            if UwAccount.exists(prior_netid):
                user = UwAccount.get(prior_netid)
                user.prev_netid = prior_netid
                user.netid = cur_uwnetid
                user.save()
                return user

        # no existing entry
        if create is True:
            return UwAccount.objects.create(netid=cur_uwnetid)
