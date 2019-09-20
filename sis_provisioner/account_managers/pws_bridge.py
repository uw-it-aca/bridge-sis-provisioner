"""
This class will load all the users in gws uw_member, uw_afiliate groups.
Check against PWS Person, apply high priority changes.
1. Add new user account (to DB and Bridge)
2. Restore and update disabled/terminated account
3. Update account if uwnetid has changed
"""

from datetime import datetime, timedelta
import logging
import traceback
from uw_bridge.models import BridgeUser, BridgeCustomField
from sis_provisioner.dao.hrp import get_worker
from sis_provisioner.dao.uw_account import save_uw_account
from sis_provisioner.dao.pws import get_updated_persons
from sis_provisioner.models.work_positions import WORK_POSITION_FIELDS
from sis_provisioner.util.settings import (
    get_total_work_positions_to_load, get_person_changed_window)
from sis_provisioner.account_managers import (
    get_full_name, get_email, get_job_title, normalize_name,
    GET_POS_ATT_FUNCS, get_supervisor_bridge_id, get_custom_field_value)
from sis_provisioner.account_managers.gws_bridge import GwsBridgeLoader


logger = logging.getLogger(__name__)


class PwsBridgeLoader(GwsBridgeLoader):

    def __init__(self, worker, clogger=logger):
        super(PwsBridgeLoader, self).__init__(worker, clogger)
        self.data_source = "GWS uw_members group"

    def fetch_users(self):
        return get_updated_persons(self.get_changed_since_datetime())

    def get_changed_since_datetime(self):
        return datetime.now() - timedelta(minutes=get_person_changed_window())

    def process_users(self):
        """
        Process potential learners in GWS, add new users or update
        the exsiting users
        """
        for person in self.get_users_to_process():
            if not (self.is_invalid_person(person.uwnetid, person) and
                    self.in_uw_groups(person.uwnetid)):
                continue
            self.total_checked_users += 1
            self.take_action(person, priority_changes_only=False)
