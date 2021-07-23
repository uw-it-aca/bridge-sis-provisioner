# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from abc import ABCMeta, abstractmethod
from sis_provisioner.util.log import log_exception


class Worker:

    """
    The Worker is an abstract class for applying actions
    on the user account in Bridge.
    """

    __metaclass__ = ABCMeta

    def __init__(self, logger):
        self.logger = logger
        self.errors = []

    def append_error(self, message):
        self.errors.append(message)

    def get_error_report(self):
        return ',\n'.join(self.errors)

    def handle_exception(self, msg, ex, traceback):
        log_exception(self.logger, msg, traceback.format_exc(chain=False))
        self.append_error("{0} ==> {1}\n".format(msg, str(ex)))

    def has_err(self):
        return len(self.errors) > 0

    @abstractmethod
    def add_new_user(self, uw_account, person, hrp_wkr):
        """
        Add a new user into Bridge
        :param uw_account: a valid UwAccount object.
        """

    @abstractmethod
    def delete_user(self, bridge_account):
        """
        Delete an active existing user in Bridge
        :param bridge_account: a valid BridgeUser object.
        :return True if successful.
        """

    @abstractmethod
    def restore_user(self, uw_account):
        """
        Restore a deleted existing user and update it in Bridge
        :param uw_account: a valid UwAccount object.
        :return: a valid BridgeUser object.
        """

    @abstractmethod
    def update_uid(self, uw_account):
        """
        Change the UID on an existing user in Bridge
        :param uw_account: a valid UwAccount object.
        :return True if successful.
        """

    @abstractmethod
    def update_user(self, bridge_account, uw_account, person, hrp_wkr):
        """
        Update the existing BridgeUser data (including change uid and regid)
        :param bridge_account: a validBridgeUser object.
        :param uw_account: a valid UwAccount object.
        :param person: a valid PWS Person object
        """

    @abstractmethod
    def get_new_user_count(self):
        """
        :return: total number of new users added successfully
        """

    @abstractmethod
    def get_netid_changed_count(self):
        """
        :return: total number of users whose netid being changed successfully
        """

    @abstractmethod
    def get_deleted_count(self):
        """
        :return: total number of users being deleted successfully
        """

    @abstractmethod
    def get_restored_count(self):
        """
        :return: total number of users being restored successfully
        """

    @abstractmethod
    def get_updated_count(self):
        """
        :return: total number of users being updated successfully
        """
