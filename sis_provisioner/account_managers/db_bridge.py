"""
This class will validate all the user accounts in the database
against gws uw_member group and pws person, and update the
accounts via the given worker.
"""

import logging
import traceback
from restclients.exceptions import DataFailureException
from sis_provisioner.dao.user import save_user
from sis_provisioner.util.log import log_exception
from sis_provisioner.account_managers import fetch_users_from_db,\
    get_validated_user, LEFT_UW, DISALLOWED
from sis_provisioner.account_managers.gws_bridge import GwsBridgeLoader


logger = logging.getLogger(__name__)


class UserUpdater(GwsBridgeLoader):

    def __init__(self, worker, clogger=logger, include_hrp=False):
        super(UserUpdater, self).__init__(worker, clogger, include_hrp)

    def fetch_users(self):
        self.data_source = "DB"
        return fetch_users_from_db(logger)

    def process_users(self):
        for uw_bri_user in self.get_users_to_process():
            try:
                person, validation_status = get_validated_user(
                    self.logger,
                    uw_bri_user.netid,
                    uwregid=uw_bri_user.regid,
                    check_gws=True)
            except DataFailureException as ex:
                log_exception(
                    logger,
                    "Validate user (%s) failed, skip!" % uw_bri_user,
                    traceback.format_exc())
                self.worker.append_error(
                    "Validate user %s: %s" % (uw_bri_user, ex))
                continue

            if person is None:
                if uw_bri_user.disabled:
                    self.logger.info("%s has been disabled!" % uw_bri_user)
                    continue
                self.logger.info(
                    "%s is no longer a valid learner, terminate!" %
                    uw_bri_user)
                self.terminate(uw_bri_user, validation_status)
            else:
                self.take_action(person)

    def terminate(self, uw_bri_user, validation_status):
        """
        @param uw_bri_user the UwBridgeUser object of an existing account
        Check the existing users for termination.
        If the user's termination date has been reached, return True
        """
        if validation_status == LEFT_UW:
            self.logger.info(
                "%s: has left UW, set terminate date" % uw_bri_user)
            uw_bri_user.save_terminate_date(graceful=True)

        elif validation_status == DISALLOWED:
            # rare case
            self.logger.info(
                "Not a personal netid, worker.delete %s" % uw_bri_user)
            self.worker.delete_user(uw_bri_user)

        if uw_bri_user.is_stalled():
            # stalled user can be removed now
            self.logger.info("%s is a stalled account!" % uw_bri_user)
            uw_bri_user.save_terminate_date(graceful=False)

        if uw_bri_user.passed_terminate_date() and\
                not uw_bri_user.disabled:
            self.logger.info(
                "Passed the terminate date, worker.delete %s" % uw_bri_user)
            self.worker.delete_user(uw_bri_user)
