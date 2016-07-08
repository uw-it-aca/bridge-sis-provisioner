import logging
import traceback
from restclients.exceptions import DataFailureException
from sis_provisioner.dao.gws import get_uw_members
from sis_provisioner.dao.user import create_user
from sis_provisioner.util.log import log_exception


logger = logging.getLogger(__name__)


class LoadUsers:

    def __init__(self):
        self.invalid_count = 0
        self.total_count = 0
        self.users = []

    def fetch_all(self):
        try:
            members = get_uw_members()
        except DataFailureException:
            log_exception(logger,
                          "Failed to get uw_member from GWS",
                          traceback.format_exc())
            return

        self.total_count = len(members)

        for uwnetid in members:
            try:
                user = create_user(uwnetid)
                self.users.append(user)
            except DataFailureException as ex:
                log_exception(logger,
                              "Failed to create user (%s)" % uwnetid,
                              traceback.format_exc())
                self.invalid_count = self.invalid_count + 1
                continue

        # print "Total uw member processed: %d" % self.total_count
        # print "Total loaded: %d" % (self.total_count - self.invalid_count)
        # print "Invalid member: %d" % self.invalid_count

    def get_total_count(self):
        return self.total_count

    def get_invalid_count(self):
        return self.invalid_count

    def get_total_loaded_count(self):
        return self.get_total_count() - self.get_invalid_count()
