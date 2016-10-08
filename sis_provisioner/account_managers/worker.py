"""
The Worker is an abstract class for applying actions
on the user account in Bridge.
"""

import traceback
from abc import ABCMeta, abstractmethod


class Worker:
    __metaclass__ = ABCMeta

    def __init__(self):
        self.errors = []

    def append_error(self, message):
        self.errors.append(message)

    def get_error_report(self):
        return ',\n'.join(self.errors)

    def has_err(self):
        return len(self.errors) > 0

    @abstractmethod
    def add_new_user(self, uw_bri_user):
        """
        Add a new user into Bridge
        @param uw_bri_user a valid UwBridgeUser object.
        @return True if successful.
        """
        pass

    @abstractmethod
    def delete_user(self, user_to_del):
        """
        Delete an active existing user in Bridge
        @param user_to_del a valid UwBridgeUser object.
        @return True if successful.
        """
        pass

    @abstractmethod
    def restore_user(self, uw_bri_user):
        """
        Restore a deleted existing user and update it in Bridge
        @param uw_bri_user a valid UwBridgeUser object.
        @return True if successful.
        """
        pass

    @abstractmethod
    def update_uid(self, uw_bri_user):
        """
        Change the UID on an existing user in Bridge
        @param uw_bri_user a valid UwBridgeUser object.
        @return True if successful.
        """
        pass

    @abstractmethod
    def update_user(self, uw_bri_user):
        """
        Update the existing user in Bridge (including change uid and regid)
        @param uw_bri_user a valid UwBridgeUser object.
        @return True if successful.
        """
        pass

    @abstractmethod
    def get_new_user_count(self):
        """
        @return total number of new users added successfully
        """
        pass

    @abstractmethod
    def get_netid_changed_count(self):
        """
        @return total number of users whose netid being changed successfully
        """
        pass

    @abstractmethod
    def get_regid_changed_count(self):
        """
        @return total number of users whose regid being changed,
        netid not changed successfully
        """
        pass

    @abstractmethod
    def get_deleted_count(self):
        """
        @return total number of users being deleted successfully
        """
        return self.total_deleted_count

    @abstractmethod
    def get_restored_count(self):
        """
        @return total number of users being restored successfully
        """
        pass
