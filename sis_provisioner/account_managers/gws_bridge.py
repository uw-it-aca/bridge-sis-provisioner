"""
This class will load all the users in gws uw_member group, check
against pws person, update their database records and bridge
accounts via the given worker.
"""

import logging
import traceback
from restclients.exceptions import DataFailureException
from restclients.models.bridge import BridgeUser
from sis_provisioner.models import UwBridgeUser
from sis_provisioner.account_managers import get_validated_user, VALID
from sis_provisioner.account_managers.loader import Loader
from sis_provisioner.util.log import log_exception
from sis_provisioner.dao.bridge import is_active_user_exist
from sis_provisioner.dao.user import save_user


logger = logging.getLogger(__name__)


class GwsBridgeLoader(Loader):

    def __init__(self, worker, clogger=logger, include_hrp=False):
        super(GwsBridgeLoader, self).__init__(worker, clogger, include_hrp)

    def fetch_users(self):
        self.data_source = "GWS uw_members group"
        return self.get_users_in_gws()

    def process_users(self):
        """
        Process potential learners in GWS, add new users or update
        the exsiting users
        """
        for uwnetid in self.get_users_to_process():
            try:
                person, validation_status = get_validated_user(
                    self.logger, uwnetid)
            except DataFailureException as ex:
                self.worker.append_error(
                    "Validate user %s ==> %s" % (uwnetid, ex))
                continue
            # Ignore DISALLOWED, INVALID ones
            if person is not None and validation_status >= VALID:
                self.take_action(person)

    def take_action(self, person):
        """
        @param: person is a valid Person object
        """
        try:
            uw_bridge_user, del_user = save_user(
                person, include_hrp=self.include_hrp())
        except Exception as ex:
            uwnetid = person.uwnetid
            log_exception(self.logger,
                          "Save user %s " % uwnetid,
                          traceback.format_exc())
            self.worker.append_error("Save user %s ==> %s" % (uwnetid, ex))
            return

        if uw_bridge_user is None:
            self.add_error(
                "Save user (%s, %s) in DB ==> return None" %
                (person.uwnetid, person.uwregid))
            return

        if del_user is not None:
            # deleted from local DB as result of a merge
            self.merge_user_accounts(del_user, uw_bridge_user)

        self.apply_change_to_bridge(uw_bridge_user)

        if self.include_hrp() and uw_bridge_user.is_employee:
            self.emp_app_totals.append(uw_bridge_user.get_total_emp_apps())

    def merge_user_accounts(self, del_user, user_to_keep):
        """
        :param del_user: user to be terminated in Bridge
        :param user_to_keep: accunt to be merged to
        """
        if type(user_to_keep) == BridgeUser:
            kp_user = user_to_keep
        else:   # user_to_keep is UwBridgeUser
            exists2, kp_user = is_active_user_exist(user_to_keep.netid)
            if not exists2 or kp_user is None:
                self.logger.error("Merge %s to %s, #2 not in Bridge, skip!",
                                  del_user, user_to_keep)
                return
            user_to_keep.set_bridge_id(kp_user.bridge_id)

        if type(del_user) == BridgeUser:
            user = del_user
        else:   # type(del_user) == UwBridgeUser
            exists1, user = is_active_user_exist(del_user.netid)
            if not exists1 or user is None:
                self.logger.error("Merge %s to %s, #1 not exists in Bridge",
                                  del_user, user_to_keep)
                return
        if user.bridge_id != kp_user.bridge_id:
            self.merge_users_in_bridge(user, kp_user)

    def merge_users_in_bridge(self, user_to_del, user_to_keep):
        self.logger.info(
            "Merge Bridge users %s to %s, then delete the 1st.",
            user_to_del, user_to_keep)
        # TO add: merge learning history from user_to_del to user_to_keep
        self.logger.info("worker.delete if no history %s",
                         user_to_del)
        self.worker.delete_user(user_to_del, is_merge=True)

    def apply_change_to_bridge(self, uw_bridge_user):
        """
        @param: uw_bridge_user a valid UwBridgeUser object to take action upon
        """
        if uw_bridge_user.is_new():
            self.logger.info("worker.add_new %s", uw_bridge_user)
            self.worker.add_new_user(uw_bridge_user)

        elif uw_bridge_user.is_restore():
            self.logger.info("worker.restore %s", uw_bridge_user)
            self.worker.restore_user(uw_bridge_user)

        else:
            self.logger.info("worker.update %s", uw_bridge_user)
            self.worker.update_user(uw_bridge_user)
