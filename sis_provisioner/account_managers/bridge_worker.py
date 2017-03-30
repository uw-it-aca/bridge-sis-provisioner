"""
The BridgeWorker class will apply actions on the user account in Bridge
via the Bridge APIs.
"""

import logging
import traceback
from restclients.exceptions import DataFailureException
from sis_provisioner.dao import is_using_file_dao
from sis_provisioner.dao.bridge import add_bridge_user, change_uwnetid,\
    get_regid_from_bridge_user, delete_bridge_user, update_bridge_user,\
    restore_bridge_user
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

    def _uid_matched(self, uw_bridge_user, ret_bridge_user):
        return (ret_bridge_user is not None and
                ret_bridge_user.netid == uw_bridge_user.netid)

    def _save_bridge_id(self, uw_bridge_user, ret_bridge_user):
        if not uw_bridge_user.has_bridge_id():
            uw_bridge_user.set_bridge_id(ret_bridge_user.bridge_id)

    def _save_verified(self, uw_bridge_user, upd_counter=True):
        uw_bridge_user.save_verified()
        if upd_counter:
            self.total_loaded_count += 1

    def add_new_user(self, uw_bridge_user):
        try:
            ret_bridge_user, exist = add_bridge_user(uw_bridge_user)
            if not exist:
                if self._uid_matched(uw_bridge_user, ret_bridge_user):
                    logger.info("Created user %s in Bridge" % uw_bridge_user)
                    self.total_new_users_count += 1
                    self._save_bridge_id(uw_bridge_user, ret_bridge_user)
                    self._save_verified(uw_bridge_user)
                    return
                self.append_error("Failed to create %s\n" %
                                  uw_bridge_user.netid)
            else:
                if self._uid_matched(uw_bridge_user, ret_bridge_user):
                    logger.info("New in DB %s ==> But exists in Bridge %s",
                                uw_bridge_user, ret_bridge_user)
                    self._save_bridge_id(uw_bridge_user, ret_bridge_user)
                    uw_bridge_user.set_action_update()
                    self._update_user(uw_bridge_user)
                    return
                self.append_error("Can't create %s ==> CHECK in Bridge\n" %
                                  uw_bridge_user.netid)
        except Exception as ex:
            self._handle_exception("create", uw_bridge_user, ex, traceback)

    def delete_user(self, user_to_del, is_merge=False):
        try:
            if delete_bridge_user(user_to_del, is_merge):
                logger.info("Deleted %s from Bridge" % user_to_del)
                user_to_del.disable()
                logger.info("Disable user in DB %s", user_to_del)
                self.total_deleted_count += 1
            else:
                self.append_error("Failed to delete %s\n" %
                                  user_to_del)
        except Exception as ex:
            self._handle_exception("delete", user_to_del, ex, traceback)

    def mark_restored(self, uw_bridge_user, ret_bridge_user):
        logger.info("Restored %s in Bridge" % uw_bridge_user)
        uw_bridge_user.set_restored()
        self._save_bridge_id(uw_bridge_user, ret_bridge_user)
        self.total_restored_count += 1

    def restore_user(self, uw_bridge_user):
        try:
            ret_buser = restore_bridge_user(uw_bridge_user)
            if ret_buser is not None:

                regid = get_regid_from_bridge_user(ret_buser)

                if uw_bridge_user.netid == ret_buser.netid:
                    if regid is None or uw_bridge_user.regid == regid:
                        uw_bridge_user.set_action_update()
                    else:
                        uw_bridge_user.set_action_regid_changed()

                elif (uw_bridge_user.netid_changed() and
                      uw_bridge_user.prev_netid == ret_buser.netid):
                    pass

                elif regid is None or uw_bridge_user.regid == regid:
                    uw_bridge_user.set_prev_netid(ret_buser.netid)

                else:
                    self.append_error("Failed to restore %s\n" %
                                      uw_bridge_user)
                    return

                self.mark_restored(uw_bridge_user, ret_buser)
                self.update_user(uw_bridge_user)
            else:
                self.append_error("Failed to restore %s\n" %
                                  uw_bridge_user)
                logger.error("Failed restore %s", uw_bridge_user)

        except Exception as ex:
            self._handle_exception("restore", uw_bridge_user, ex, traceback)

    def update_user(self, uw_bridge_user):
        if not uw_bridge_user.netid_changed() or\
           self.update_uid(uw_bridge_user):
            self._update_user(uw_bridge_user)

    def update_uid(self, uw_bridge_user):
        try:
            ret_bridge_user = change_uwnetid(uw_bridge_user)
            if self._uid_matched(uw_bridge_user, ret_bridge_user):
                logger.info("Changed UID for %s in Bridge",
                            uw_bridge_user)
                uw_bridge_user.clear_prev_netid()
                self._save_bridge_id(uw_bridge_user, ret_bridge_user)
                self.total_netid_changes_count += 1
                return True

            self.append_error("Failed to Change-uid for %s\n" %
                              uw_bridge_user)
        except Exception as ex:
            self._handle_exception("change-uid", uw_bridge_user, ex, traceback)
        return False

    def _update_user(self, uw_bridge_user):
        try:
            ret = update_bridge_user(uw_bridge_user)
            if ret is None:
                # verified no change
                self._save_verified(uw_bridge_user, upd_counter=False)
            else:
                if ret:
                    logger.info("Updated user %s in Bridge",
                                uw_bridge_user)
                    if uw_bridge_user.regid_changed():
                        self.total_regid_changes_count += 1
                    self._save_verified(uw_bridge_user)
                else:
                    self.append_error("Failed to update: %s ==> restore?\n" %
                                      uw_bridge_user)
        except Exception as ex:
            self._handle_exception("update", uw_bridge_user, ex, traceback)

    def _handle_exception(self, action, uw_bridge_user,
                          ex, traceback):
        if self._not_exist(uw_bridge_user, ex):
            return
        log_exception(logger,
                      "Failed %s: %s ==>" % (action, uw_bridge_user),
                      traceback.format_exc())
        self.append_error("Failed to %s: %s ==> %s\n" %
                          (action, uw_bridge_user.netid, ex))

    def _not_exist(self, uw_bridge_user, ex):
        if isinstance(ex, DataFailureException) and\
           ex.status == 404:
            logger.info("Not exist in Bridge, delete from local DB %s" %
                        uw_bridge_user)
            uw_bridge_user.delete()
            return True
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
