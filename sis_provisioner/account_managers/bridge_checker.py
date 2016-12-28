"""
This class will load all the existing users in bridge,
validate against gws uw_member group and pws person,
and update their database records and the bridge
accounts via the given worker.
"""

import logging
import traceback
from restclients.exceptions import DataFailureException
from sis_provisioner.dao.user import get_user_from_db, save_user
from sis_provisioner.dao.bridge import get_regid_from_bridge_user
from sis_provisioner.models import UwBridgeUser
from sis_provisioner.util.log import log_exception
from sis_provisioner.account_managers import get_validated_user,\
    fetch_users_from_bridge
from sis_provisioner.account_managers.db_bridge import UserUpdater


logger = logging.getLogger(__name__)


class BridgeChecker(UserUpdater):

    def __init__(self, worker, clogger=logger, include_hrp=False):
        super(BridgeChecker, self).__init__(worker, clogger, include_hrp)

    def fetch_users(self):
        self.data_source = "Bridge"
        return fetch_users_from_bridge(logger)

    def process_users(self):
        for bridge_user in self.get_users_to_process():
            uwnetid = bridge_user.netid
            uwregid = get_regid_from_bridge_user(bridge_user)
            person = None
            try:
                person, validation_status = get_validated_user(logger,
                                                               uwnetid,
                                                               uwregid=uwregid,
                                                               check_gws=True)
            except DataFailureException as ex:
                log_exception(
                    logger,
                    "Validate user (%s) failed, skip!" % bridge_user,
                    traceback.format_exc())
                self.worker.append_error(
                    "Validate user %s: %s" % (bridge_user, ex))
                continue

            uw_bridge_user = get_user_from_db(uwnetid, uwregid)

            if person is not None:
                in_db = uw_bridge_user is not None
                logger.info("%s Bridge user in DB: %s" % (
                        "Update" if in_db else "Create", bridge_user))
                self.take_action(person, bridge_user, in_db)
                continue

            self.logger.info(
                "%s no longer a valid learner, terminate!" % bridge_user)
            if uw_bridge_user is not None:
                # The Bridge account is in our DB
                if uw_bridge_user.disabled:
                    # marked disabled, but exists as a valid user in Bridge
                    # report an inconsistent state!
                    self.add_error(
                        "Inconsistent State: %s DISABLED!" % bridge_user)
                    continue
                self.terminate(uw_bridge_user, validation_status)
                continue

            # not in local DB (created manually)
            self.add_error("Unknown Bridge user: %s" % bridge_user)

    def take_action(self, person, bridge_user, in_db=False):
        """
        Add the Bridge user (not in DB yet) into local DB
        @param person must be a valid object
        """
        try:
            uw_bridge_user, del_user = save_user(
                person, include_hrp=self.include_hrp())

            if in_db and del_user is not None:
                self.merge_user_accounts(del_user, uw_bridge_user)

            if uw_bridge_user is not None:
                if not in_db:
                    if uw_bridge_user.is_new():
                        # created manually in Bridge, now added in DB
                        uw_bridge_user.set_no_action()
                    else:
                        self.add_error(
                            "Bridge user (%s) NOT in DB, %s" % (
                                bridge_user,
                                "but save_user found it EXIST in DB"))
                        return
                else:
                    if uw_bridge_user.is_new():
                        self.add_error(
                            "Bridge user (%s) in DB, %s" % (
                                bridge_user,
                                "but save_user NOT found it"))
                        return
            else:
                self.add_error(
                    "FAILED to %s Bridge user in DB: %s" % (
                        ("update" if in_db else "create"), bridge_user))
                return

            uw_bridge_user.set_bridge_id(bridge_user.bridge_id)

            if self.changed_attributes(bridge_user, uw_bridge_user):
                self.logger.info("Update %s" % uw_bridge_user)
                self.worker.update_user(uw_bridge_user)

        except Exception as ex:
            log_exception(self.logger,
                          "Take_action failed (%s)" % bridge_user,
                          traceback.format_exc())
            self.worker.append_error(
                "Take_action failed %s: %s" % (bridge_user, ex))

    def changed_attributes(self, bridge_user, uw_bridge_user):
        if uw_bridge_user.netid_changed():
            return True

        if bridge_user.netid != uw_bridge_user.netid:
            uw_bridge_user.set_prev_netid(bridge_user.netid)
            return True

        if uw_bridge_user.regid_changed():
            return True

        regid = get_regid_from_bridge_user(bridge_user)
        if regid != uw_bridge_user.regid:
            uw_bridge_user.set_action_regid_changed()
            return True

        if uw_bridge_user.is_update():
            return True

        # current attributes 12/10/2016.
        if bridge_user.full_name != uw_bridge_user.get_display_name() or\
                bridge_user.email != uw_bridge_user.get_email():
            uw_bridge_user.set_action_update()
            return True
        return False
