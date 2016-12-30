"""
The CsvWorker class will put the user accounts in the corresponding list
based on the action to take. These lists will be used to generate csv files,
which can be imported on the Bridge UI.
"""

import logging
import traceback
from sis_provisioner.util.list_helper import get_item_counts_dict
from sis_provisioner.account_managers.worker import Worker


logger = logging.getLogger(__name__)


class CsvWorker(Worker):

    def __init__(self):
        super(CsvWorker, self).__init__()
        self.total_new_users_count = 0
        self.users_to_load = []
        self.users_changed_netid = []
        self.users_changed_regid = []
        self.users_to_del = []
        self.users_to_restore = []

    def _load_user(self, uw_bri_user):
        self.users_to_load.append(uw_bri_user)

    def add_new_user(self, uw_bri_user):
        self.total_new_users_count += 1
        self._load_user(uw_bri_user)

    def delete_user(self, user_to_del):
        self.users_to_del.append(user_to_del)

    def restore_user(self, uw_bri_user):
        self.users_to_restore.append(uw_bri_user)

    def update_user(self, uw_bri_user):
        if uw_bri_user.netid_changed():
            self.update_uid(uw_bri_user)
            return
        if uw_bri_user.regid_changed():
            self.update_regid(uw_bri_user)
            return
        self._load_user(uw_bri_user)

    def update_uid(self, uw_bri_user):
        self.users_changed_netid.append(uw_bri_user)

    def update_regid(self, uw_bri_user):
        self.users_changed_regid.append(uw_bri_user)

    def get_new_user_count(self):
        return self.total_new_users_count

    def get_deleted_count(self):
        return len(self.users_to_del)

    def get_users_to_delete(self):
        """
        return a list of UwBridgeUser objects
        """
        return self.users_to_del

    def get_loaded_count(self):
        """
        Return the number of users being added/updated to DB and
        to be loaded into Bridge
        """
        return len(self.users_to_load)

    def get_users_to_load(self):
        """
        return a list of UwBridgeUser objects
        """
        return self.users_to_load

    def get_netid_changed_count(self):
        """
        return a list of UwBridgeUser objects
        """
        return len(self.users_changed_netid)

    def get_users_netid_changed(self):
        return self.users_changed_netid

    def get_regid_changed_count(self):
        return len(self.users_changed_regid)

    def get_users_regid_changed(self):
        return self.users_changed_regid

    def get_restored_count(self):
        return len(self.users_to_restore)

    def get_users_to_restore(self):
        """
        return a list of UwBridgeUser objects
        """
        return self.users_to_restore
