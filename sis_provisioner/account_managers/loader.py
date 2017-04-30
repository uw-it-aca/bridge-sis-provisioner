"""
The Loader is an abstract class for managing user account.
"""

import logging
import traceback
import json
from abc import ABCMeta, abstractmethod
from sis_provisioner.util.list_helper import get_item_counts_dict
from sis_provisioner.account_managers import fetch_users_from_gws


class Loader:
    __metaclass__ = ABCMeta

    def __init__(self, worker, logger, include_hrp):
        """
        @param worker: is a concrete object of Worker
        """
        self.include_hrp_data = include_hrp
        self.logger = logger
        self.users_to_process = []
        self.data_source = None  # where the user is fetched from
        self.worker = worker
        self.emp_app_totals = []
        self.users_in_gws = fetch_users_from_gws(self.logger)

    def load(self):
        self.users_to_process = self.fetch_users()
        if self.get_total_count() == 0:
            self.logger.info("Not found users to process, abort!")
            return
        self.process_users()
        self.log_status()

    @abstractmethod
    def fetch_users(self):
        pass

    @abstractmethod
    def process_users(self):
        pass

    def log_status(self):
        self.logger.info("Checked %d users in %s,",
                         self.get_total_count(), self.data_source)
        if self.get_loaded_count():
            self.logger.info("total %d users loaded,",
                             self.get_loaded_count())
        if self.get_new_user_count():
            self.logger.info("%d are new users.",
                             self.get_new_user_count())
        if self.get_netid_changed_count():
            self.logger.info("%d changed their netids.",
                             self.get_netid_changed_count())
        if self.get_regid_changed_count():
            self.logger.info("%d changed their regids.",
                             self.get_regid_changed_count())
        if self.get_deleted_count():
            self.logger.info("%d users have been deleted.",
                             self.get_deleted_count())
        if self.get_restored_count():
            self.logger.info("%d users have been restored.",
                             self.get_restored_count())

        if self.has_error():
            self.logger.info("Errors: %s",
                             self.get_error_report())

        if self.include_hrp():
            counts_dict = get_item_counts_dict(self.emp_app_totals)
            self.logger.info("appointments counts: %s",
                             json.dumps(counts_dict))

    def include_hrp(self):
        return self.include_hrp_data

    def get_users_in_gws(self):
        return self.users_in_gws

    def get_total_count(self):
        return len(self.users_to_process)

    def get_users_to_process(self):
        return self.users_to_process

    def get_loaded_count(self):
        """
        @return total number of users updated successfully
        """
        return self.worker.get_loaded_count()

    def get_new_user_count(self):
        """
        @return total number of new users added successfully
        """
        return self.worker.get_new_user_count()

    def get_netid_changed_count(self):
        """
        @return total number of users whose netid being changed
        and loaded successfully
        """
        return self.worker.get_netid_changed_count()

    def get_regid_changed_count(self):
        """
        @return total number of users whose regid being changed,
        netid not changed and loaded successfully
        """
        return self.worker.get_regid_changed_count()

    def get_deleted_count(self):
        """
        @return total number of users being deleted successfully
        """
        return self.worker.get_deleted_count()

    def get_restored_count(self):
        """
        @return total number of users being restored successfully
        """
        return self.worker.get_restored_count()

    def get_error_report(self):
        return self.worker.get_error_report()

    def has_error(self):
        return self.worker.has_err()

    def add_error(self, err_msg):
        self.logger.error(err_msg)
        self.worker.append_error(err_msg)
