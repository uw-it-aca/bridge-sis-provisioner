"""
The BridgeWorker class will apply actions on the user account in Bridge
via the Bridge APIs.
"""

import logging
import traceback
from sis_provisioner.dao import is_using_file_dao
from sis_provisioner.dao.bridge import add_bridge_user,\
    change_uwnetid, delete_bridge_user, update_bridge_user, restore_bridge_user
from sis_provisioner.util.log import log_exception
from sis_provisioner.account_managers.worker import Worker


logger = logging.getLogger(__name__)


class BridgeWorker(Worker):

    def __init__(self):
        super(BridgeWorker, self).__init__()
        self.total_deleted_count = 0
        self.total_netid_changes_count = 0
        self.total_regid_changes_count = 0
        self.total_new_users_count = 0
        self.total_restored_count = 0
        self.total_loaded_count = 0

    def _verify_resp(self, return_users, uw_bri_user):
        return return_users is not None and len(return_users) == 1 and\
            (return_users[0].netid == uw_bri_user.netid or
             is_using_file_dao())

    def add_new_user(self, uw_bri_user):
        try:
            ret_users = add_bridge_user(uw_bri_user)
            if self._verify_resp(ret_users, uw_bri_user):
                uw_bri_user.set_bridge_id(ret_users[0].bridge_id)
                logger.info("Created user %s in Bridge" % uw_bri_user)
                self.save_verified(uw_bri_user)
                self.total_new_users_count += 1
                return
            self.append_error("Add New failed on %s" % uw_bri_user)

        except Exception as ex:
            log_exception(logger,
                          "Failed to create user (%s)" % uw_bri_user,
                          traceback.format_exc())
            self.append_error("Create failed on %s: %s" % (
                    uw_bri_user, ex))

    def delete_user(self, user_to_del):
        try:
            if delete_bridge_user(user_to_del):
                logger.info("Deleted user %s from Bridge" % user_to_del)
                self.total_deleted_count += 1
                return
            self.append_error("Delete failed on %s" % user_to_del)

        except Exception as ex:
            log_exception(logger,
                          "Failed to delete user (%s)" % user_to_del,
                          traceback.format_exc())
            self.append_error("Delete failed on %s: %s" % (
                    user_to_del, ex))

    def restore_user(self, uw_bri_user):
        if self._restore_user(uw_bri_user):
            if self._update_user(uw_bri_user):
                self.save_verified(uw_bri_user)

    def _restore_user(self, uw_bri_user):
        try:
            ret_users = restore_bridge_user(uw_bri_user)
            if self._verify_resp(ret_users, uw_bri_user):
                logger.info("Restored user %s in Bridge" % uw_bri_user)
                self.total_restored_count += 1
                return True
            self.append_error("Restore failed on %s" % uw_bri_user)

        except Exception as ex:
            log_exception(logger,
                          "Failed to restore user (%s)" % uw_bri_user,
                          traceback.format_exc())
            self.append_error("Restore failed on %s: %s" % (
                    uw_bri_user, ex))
        return False

    def update_user(self, uw_bri_user):
        if not uw_bri_user.netid_changed() or self.update_uid(uw_bri_user):
            if self._update_user(uw_bri_user):
                self.save_verified(uw_bri_user)

    def update_uid(self, uw_bri_user):
        try:
            return_users = change_uwnetid(uw_bri_user)
            if self._verify_resp(return_users, uw_bri_user):
                logger.info("Changed UID of user %s in Bridge" % uw_bri_user)
                self.total_netid_changes_count += 1
                return True
            self.append_error("Change-UID failed on %s" % uw_bri_user)

        except Exception as ex:
            log_exception(logger,
                          "Failed to change-uid for user (%s)" % uw_bri_user,
                          traceback.format_exc())
            self.append_error("Change uid failed on %s: %s" % (
                    uw_bri_user, ex))
        return False

    def _update_user(self, uw_bri_user):
        try:
            return_users = update_bridge_user(uw_bri_user)
            if self._verify_resp(return_users, uw_bri_user):
                logger.info("Updated user %s in Bridge" % uw_bri_user)
                if uw_bri_user.regid_changed():
                    self.total_regid_changes_count += 1
                return True
            self.append_error("Update failed on %s" % uw_bri_user)

        except Exception as ex:
            log_exception(logger,
                          "Failed to update user (%s)" % uw_bri_user,
                          traceback.format_exc())
            self.append_error("Update failed on %s: %s" % (
                    uw_bri_user, ex))
        return False

    def get_new_user_count(self):
        return self.total_new_users_count

    def get_netid_changed_count(self):
        return self.total_netid_changes_count

    def get_regid_changed_count(self):
        return self.total_regid_changes_count

    def get_restored_count(self):
        return self.total_restored_count

    def get_deleted_count(self):
        return self.total_deleted_count

    def get_loaded_count(self):
        return self.total_loaded_count

    def save_verified(self, uw_bridge_user):
        uw_bridge_user.save_verified()
        self.total_loaded_count += 1
