"""
This class will load all the users in gws uw_member group, check
against pws person, update their database records and bridge
accounts via the given worker.
"""

import logging
import traceback
from sis_provisioner.account_managers import fetch_users_from_gws,\
    get_validated_user
from sis_provisioner.account_managers.loader import Loader
from sis_provisioner.util.log import log_exception
from sis_provisioner.dao.bridge import delete_bridge_user
from sis_provisioner.dao.user import save_user


logger = logging.getLogger(__name__)


class GwsBridgeLoader(Loader):

    def __init__(self, worker, clogger=logger, include_hrp=False):
        super(GwsBridgeLoader, self).__init__(worker, clogger, include_hrp)
        self.total_loaded_count = 0  # updated

    def fetch_users(self):
        self.data_source = "GWS uw_members group"
        return fetch_users_from_gws(self.logger)

    def process_users(self):
        """
        Validate the users and Update the corresponding records
        """
        for uwnetid in self.get_users_to_process():
            try:
                person, validation_status = get_validated_user(
                    self.logger, uwnetid)
            except DataFailureException:
                log_exception(
                    logger,
                    "validate user (%s) failed, skip!" % uwnetid,
                    traceback.format_exc())
                self.worker.append_error(
                    "validate user %s: %s" % (uwnetid, ex))
                continue

            if person is None:
                self.logger.info(
                    "%s is not a valid learner, skip!" % uwnetid)
                continue
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
                          "Failed to save user (%s)" % uwnetid,
                          traceback.format_exc())
            self.worker.append_error("save user %s: %s" % (uwnetid, ex))
            return

        if del_user is not None:
            self.merge_user_accounts(del_user, uw_bridge_user)

        self.apply_change_to_bridge(uw_bridge_user)

        if self.include_hrp() and uw_bridge_user.is_employee:
            self.emp_app_totals.append(uw_bridge_user.get_total_emp_apps())

    def merge_user_accounts(self, del_user, uw_bridge_user):
        # TO-DO:
        # merge learning history from del_user to uw_bridge_user
        # delete del_user
        self.logger.info("Delete %s" % del_user)
        self.worker.delete_user(del_user)

    def apply_change_to_bridge(self, uw_bridge_user):
        """
        @param: uw_bridge_user a valid UwBridgeUser object to take action upon
        """
        if uw_bridge_user is None or uw_bridge_user.no_action():
            return

        loaded = False
        if uw_bridge_user.is_new():
            loaded = self.worker.add_new_user(uw_bridge_user)
        elif uw_bridge_user.is_restore():
            loaded = self.worker.restore_user(uw_bridge_user)
        else:
            loaded = self.worker.update_user(uw_bridge_user)

        if loaded:
            uw_bridge_user.save_verified()
            self.total_loaded_count += 1

    def get_loaded_count(self):
        return self.total_loaded_count
