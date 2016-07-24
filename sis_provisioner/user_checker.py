import logging
import traceback
from restclients.exceptions import DataFailureException
from sis_provisioner.dao.pws import get_person_by_regid
from sis_provisioner.dao.user import get_all_users, delete_user
from sis_provisioner.loader import AbsLoader
from sis_provisioner.util.log import log_exception


logger = logging.getLogger(__name__)


class PurgeUserLoader(AbsLoader):

    def __init__(self):
        pass

    def init_set(self):
        self.total_count = 0
        self.users_left_uw = []
        self.users_to_del = []

    def fetch_all(self):
        self.init_set()
        self.delete_terminated_users()

    def include_hrp(self):
        return False

    def get_total_count(self):
        return self.total_count

    def get_delete_count(self):
        return len(self.users_to_del)

    def get_users_to_delete(self):
        return self.users_to_del

    def get_users_left_uw_count(self):
        return len(self.users_left_uw)

    def get_users_left_uw(self):
        return self.users_left_uw

    def delete_terminated_users(self):
        """
        Check the existing users marked for termination.
        If their terminate date is reached, delete them from the DB.
        """
        existing_users = get_all_users()
        self.total_count = len(existing_users)
        for user in existing_users:
            self.check_auser(user)

        logger.info("Checked %d users in DB," % self.total_count)
        logger.info("Found %d users left UW," %
                    self.get_users_left_uw_count())
        logger.info("Deleted %d users from DB." % self.get_delete_count())
        if self.get_delete_count() > 0:
            logger.info(
                "Users who should be removed from Bridg asap: %s" %
                ','.join(self.get_users_to_delete()))

    def check_auser(self, user):
        """
        Check the existing user against PWS, set a termination date on
        those no longer in PWS.
        """
        uwnetid = user.netid
        try:
            get_person_by_regid(user.regid)
            user.clear_terminate_date()
        except DataFailureException as ex:
            if ex.status == 301:
                # renamed uwnetid should be removed immediately
                logger.error("%s has been renamed!" % uwnetid)
                user.save_terminate_date(graceful=False)
            elif ex.status == 404:
                logger.error("%s became an invalid netid!" % uwnetid)
                user.save_terminate_date(graceful=True)
                self.users_left_uw.append(uwnetid)
            else:
                log_exception(logger,
                              "pws.person(%s) failed" % uwnetid,
                              traceback.format_exc())
                if user.is_stalled():
                    # stalled user can be removed now
                    logger.error("%s is stalled!" % uwnetid)
                    user.save_terminate_date(graceful=False)

        if user.passed_terminate_date():
            netids_removed = delete_user(uwnetid)
            logger.error("Removed %s from DB!" % uwnetid)
            if len(netids_removed) != 1:
                logger.error("Delete user (%s) found %d records" % (
                        uwnetid, len(netids_removed)))
            self.users_to_del.append(uwnetid)
