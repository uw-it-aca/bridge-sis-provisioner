"""
This class will check the users in DB, if the action on a user record failed
in the last load, re-apply it.
"""

import logging
from sis_provisioner.dao.user import save_user
from sis_provisioner.account_managers.db_bridge import UserUpdater


logger = logging.getLogger(__name__)


class Reloader(UserUpdater):

    def __init__(self, worker, clogger=logger, include_hrp=False):
        super(UserUpdater, self).__init__(worker, clogger, include_hrp)

    def process_users(self):
        for uw_bri_user in self.get_users_to_process():

            if uw_bri_user.passed_terminate_date() and\
                    not uw_bri_user.disabled:
                if self.worker.delete_user(uw_bri_user):
                    logger.info("Disable user in db %s" % uw_bri_user)
                    uw_bri_user.disable()
            else:
                self.apply_change_to_bridge(uw_bri_user)
