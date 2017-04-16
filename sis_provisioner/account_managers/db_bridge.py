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
    get_validated_user, LEFT_UW, DISALLOWED, INVALID, VALID
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
                    users_in_gws=self.get_users_in_gws())
            except DataFailureException as ex:
                self.worker.append_error(
                    "Validate user %s ==> %s" % (uw_bri_user, ex))
                continue

            if person is not None and validation_status == VALID:
                self.take_action(person)
            else:
                self.terminate(uw_bri_user, validation_status)

    def terminate(self, uw_bri_user, validation_status):
        """
        @param uw_bri_user the UwBridgeUser object of an existing account
        Check the existing users for termination.
        If the user's termination date has been reached, disable user.
        """
        if validation_status == LEFT_UW:
            if uw_bri_user.disabled:
                self.logger.info("%s left, already disabled!", uw_bri_user)
                return

            if not uw_bri_user.has_terminate_date():
                self.logger.info("%s: has left UW, set terminate date",
                                 uw_bri_user)
                uw_bri_user.save_terminate_date(graceful=True)

        elif validation_status <= DISALLOWED:
            # rare case
            self.logger.info(
                "Not valid personal netid, worker.delete %s" % uw_bri_user)
            self.worker.delete_user(uw_bri_user)

        else:
            self.logger.error("Invalid %s (status: %s), check in DB!",
                              uw_bri_user, validation_status)
            return

        if uw_bri_user.is_stalled():
            self.logger.info("Stalled user %s, delete!" % uw_bri_user)
            uw_bri_user.save_terminate_date(graceful=False)

        if uw_bri_user.passed_terminate_date() and\
                not uw_bri_user.disabled:
            self.logger.info(
                "Passed terminate date, worker.delete %s" % uw_bri_user)
            self.worker.delete_user(uw_bri_user)
