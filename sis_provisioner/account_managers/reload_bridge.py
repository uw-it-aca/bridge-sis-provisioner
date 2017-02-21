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

        for uw_bridge_user in self.get_users_to_process():

            if uw_bridge_user.is_restore():
                logger.info("worker.restore %s" % uw_bridge_user)
                self.worker.restore_user(uw_bridge_user)

            elif uw_bridge_user.passed_terminate_date():

                if not uw_bridge_user.disabled:
                    logger.info("worker.delete %s" % uw_bridge_user)
                    self.worker.delete_user(uw_bridge_user)

            elif uw_bridge_user.is_new():
                self.logger.info("worker.add_new %s", uw_bridge_user)
                self.worker.add_new_user(uw_bridge_user)

            else:
                self.logger.info("worker.update %s", uw_bridge_user)
                self.worker.update_user(uw_bridge_user)
