"""
This class will update user account upon the changes in PWS
"""

from datetime import datetime, timedelta
import logging
from sis_provisioner.dao.pws import get_updated_persons
from sis_provisioner.util.settings import get_person_changed_window
from sis_provisioner.account_managers.gws_bridge import GwsBridgeLoader

logger = logging.getLogger(__name__)


class PwsBridgeLoader(GwsBridgeLoader):

    def __init__(self, worker, clogger=logger):
        super(PwsBridgeLoader, self).__init__(worker, clogger)
        self.data_source = "Person updates"

    def fetch_users(self):
        return get_updated_persons(self.get_changed_since_datetime())

    def get_changed_since_datetime(self):
        return datetime.now() - timedelta(minutes=get_person_changed_window())

    def process_users(self):
        for person in self.get_users_to_process():
            if (self.is_invalid_person(person.uwnetid, person) or
                    not self.in_uw_groups(person.uwnetid)):
                continue
            self.total_checked_users += 1
            self.take_action(person)
