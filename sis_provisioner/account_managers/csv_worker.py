"""
The CsvWorker class will put the user accounts in the corresponding list
based on the action to take. These lists will be used to generate csv files,
which can be imported on the Bridge UI.
"""

import logging
from sis_provisioner.dao.bridge import get_user_by_bridgeid
from sis_provisioner.account_managers import (
    get_bridge_user_to_add, get_bridge_user_to_upd)
from sis_provisioner.account_managers.worker import Worker


logger = logging.getLogger(__name__)


class CsvWorker(Worker):

    def __init__(self):
        super(CsvWorker, self).__init__()
        self.total_new_users_count = 0
        self.users_to_load = []
        self.users_changed_netid = []
        self.users_to_del = []
        self.users_to_restore = []

    def add_new_user(self, uw_account, person):
        self.total_new_users_count += 1
        self.users_to_load.append(get_bridge_user_to_add(person))

    def delete_user(self, bridge_account):
        self.users_to_del.append(bridge_account)
        logger.info("Add user {0} to delete csv file".format(bridge_account))

    def restore_user(self, uw_account):
        pass
        # bridge_user = get_user_by_bridgeid(uw_account.netid,
        # exclude_deleted=False)
        # self.users_to_restore.append(bridge_user)
        # logger.info("Add user {0} to restore csv file".format(bridge_user))

    def update_user(self, bridge_account, uw_account, person):
        user_data = get_bridge_user_to_upd(person, bridge_account)
        if uw_account.netid_changed():
            self.update_uid(user_data)
            return
        self.users_to_load.append(user_data)

    def update_uid(self, bridge_user_data):
        self.users_changed_netid.append(bridge_user_data)
        logger.info(
            "Add user {0} to changed_netid csv file".format(bridge_user_data))

    def get_new_user_count(self):
        return self.total_new_users_count

    def get_deleted_count(self):
        return len(self.users_to_del)

    def get_users_to_delete(self):
        """
        return a list of UwAccount objects
        """
        return self.users_to_del

    def get_updated_count(self):
        """
        Return the number of users being added/updated to DB and
        to be loaded into Bridge
        """
        return len(self.users_to_load)

    def get_users_to_load(self):
        """
        return a list of UwAccount objects
        """
        return self.users_to_load

    def get_netid_changed_count(self):
        """
        return a list of UwAccount objects
        """
        return len(self.users_changed_netid)

    def get_users_netid_changed(self):
        return self.users_changed_netid

    def get_restored_count(self):
        return len(self.users_to_restore)

    def get_users_to_restore(self):
        """
        return a list of UwAccount objects
        """
        return self.users_to_restore
