import logging
import traceback
from restclients.exceptions import DataFailureException
from sis_provisioner.dao.gws import get_uw_members
from sis_provisioner.dao.user import create_user
from sis_provisioner.util.log import log_exception


logger = logging.getLogger(__name__)


class LoadUsers:

    def __init__(self, include_hrp=False):
        self.invalid_count = 0
        self.total_count = 0
        self.users = []
        self.include_hrp_data = include_hrp

    def fetch_all(self):
        try:
            members = get_uw_members()
        except Exception:
            log_exception(logger,
                          "Failed to get uw_member from GWS",
                          traceback.format_exc())
            return

        self.total_count = len(members)

        for uwnetid in members:
            try:
                user = create_user(uwnetid,
                                   include_hrp=self.include_hrp_data)
                self.users.append(user)
            except Exception as ex:
                log_exception(logger,
                              "Failed to create user (%s)" % uwnetid,
                              traceback.format_exc())
                self.invalid_count = self.invalid_count + 1
                continue
        logger.info("Finish loading %d users." % self.get_user_count())

    def include_hrp(self):
        return self.include_hrp_data

    def get_total_count(self):
        return self.total_count

    def get_invalid_count(self):
        return self.invalid_count

    def get_user_count(self):
        return self.get_total_count() - self.get_invalid_count()

    def get_users(self):
        return self.users
