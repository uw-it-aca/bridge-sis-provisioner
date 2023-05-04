# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
The Loader is an abstract class for managing user account.
"""

import logging
import traceback
import json
from abc import ABCMeta, abstractmethod
from restclients_core.exceptions import DataFailureException
from sis_provisioner.dao.gws import get_potential_users
from sis_provisioner.util.log import log_exception
from sis_provisioner.util.settings import errors_to_abort_loader


class Loader:
    __metaclass__ = ABCMeta

    def __init__(self, worker, logger):
        """
        @param worker: is a concrete object of Worker
        """
        self.logger = logger
        self.users_to_process = []
        self.total_checked_users = 0
        self.data_source = None  # where the user is fetched from
        self.worker = worker
        self.gws_user_set = get_potential_users()  # DataFailureException

    def load(self):
        self.users_to_process = self.fetch_users()
        if self.get_total_count() == 0:
            self.logger.info("Not found users to process, abort!")
            return
        self.logger.info("PROCESS {} of {}".format(
            self.get_total_count(), self.data_source))
        self.process_users()
        self.log_status()

    def is_invalid_person(self, uwnetid, person):
        if person is None:
            self.logger.error(
                "{0} NOT in PWS, skip!".format(uwnetid))
            return True
        if person.is_test_entity:
            self.logger.error(
                "{0} IsTestEntity in PWS, skip!".format(uwnetid))
            return True
        return False

    def in_uw_groups(self, uwnetid):
        return uwnetid in self.gws_user_set

    @abstractmethod
    def fetch_users(self):
        pass

    @abstractmethod
    def process_users(self):
        pass

    def log_status(self):
        self.logger.info("Checked {0:d} users in {1},".format(
                         self.get_total_checked_users(), self.data_source))

        if self.get_new_user_count():
            self.logger.info("{0:d} are new users.".format(
                             self.get_new_user_count()))

        if self.get_netid_changed_count():
            self.logger.info("{0:d} changed their netids.".format(
                             self.get_netid_changed_count()))

        if self.get_deleted_count():
            self.logger.info("{0:d} users have been deleted.".format(
                             self.get_deleted_count()))

        if self.get_restored_count():
            self.logger.info("{0:d} users have been restored.".format(
                             self.get_restored_count()))

        if self.get_updated_count():
            self.logger.info("total {0:d} users updated,".format(
                             self.get_updated_count()))

        if self.has_error():
            self.logger.info("ERROR Report: {0}".format(
                             self.get_error_report()))

    def get_total_count(self):
        return len(self.users_to_process)

    def get_total_checked_users(self):
        return self.total_checked_users

    def get_users_to_process(self):
        return self.users_to_process

    def get_new_user_count(self):
        """
        @return total number of new users added successfully
        """
        return self.worker.get_new_user_count()

    def get_deleted_count(self):
        """
        @return total number of users being deleted successfully
        """
        return self.worker.get_deleted_count()

    def get_netid_changed_count(self):
        """
        @return total number of users whose netid being changed successfully
        """
        return self.worker.get_netid_changed_count()

    def get_restored_count(self):
        """
        @return total number of users being restored successfully
        """
        return self.worker.get_restored_count()

    def get_updated_count(self):
        """
        @return total number of users updated successfully
        """
        return self.worker.get_updated_count()

    def get_error_report(self):
        return self.worker.get_error_report()

    def has_error(self):
        return self.worker.has_err()

    def add_error(self, err_msg):
        self.logger.error(err_msg)
        self.worker.append_error("{0}\n".format(err_msg))

    def handle_exception(self, msg, ex, traceback):
        log_exception(self.logger, msg, traceback.format_exc(chain=False))

        self.worker.append_error("{0} ==> {1}\n".format(msg, str(ex)))

        if (isinstance(ex, DataFailureException) and
                ex.status in errors_to_abort_loader()):
            raise
