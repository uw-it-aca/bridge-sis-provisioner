"""
This class will load all the existing users in bridge,
validate against gws uw_member group and pws person,
and update their database records and the bridge
accounts via the given worker.
"""

import logging
import traceback
from restclients.exceptions import DataFailureException
from sis_provisioner.dao.user import get_users_from_db, save_user
from sis_provisioner.dao.bridge import get_regid_from_bridge_user
from sis_provisioner.models import UwBridgeUser
from sis_provisioner.util.log import log_exception
from sis_provisioner.account_managers import get_validated_user,\
    fetch_users_from_bridge, INVALID, NO_CHANGE
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
            try:
                person, validation_status = get_validated_user(
                    logger,
                    uwnetid,
                    uwregid=uwregid,
                    users_in_gws=self.get_users_in_gws())
            except DataFailureException as ex:
                log_exception(
                    logger,
                    "Validate user (%s) failed, skip!" % bridge_user,
                    traceback.format_exc())
                self.worker.append_error(
                    "Validate user %s ==> %s" % (bridge_user, ex))
                continue

            if validation_status == INVALID:
                continue

            uw_bri_users = get_users_from_db(bridge_user.bridge_id,
                                             uwnetid,
                                             uwregid)
            in_db = len(uw_bri_users) > 0
            for user in uw_bri_users:
                if person.uwregid != user.regid and\
                   person.uwnetid != user.netid:
                    self.add_error(
                        "Bridge %s not match local record %s" %
                        (bridge_user, user))

            if person is not None and validation_status >= NO_CHANGE:
                logger.info("%s Bridge user %s in local DB",
                            "Update" if in_db else "Create", bridge_user)
                self.take_action(person, bridge_user, in_db)
                continue

            self.logger.info("No longer a valid learner: %s", bridge_user)
            if not in_db:
                # not in local DB (created manually)
                self.add_error("Unknown Bridge user: %s" % bridge_user)
                continue

            for user in uw_bri_users:
                if bridge_user.bridge_id == user.bridge_id and\
                   uwregid == user.regid and\
                   uwnetid == user.netid:
                    self.terminate(user, validation_status)
                else:
                    self.add_error(
                        "Bridge %s not match local record %s" %
                        (bridge_user, user))

    def take_action(self, person, bridge_user, in_db=False):
        """
        Add the Bridge user (not in DB yet) into local DB
        @param person must be a valid object
        """
        try:
            uw_bridge_user, del_user = save_user(
                person, include_hrp=self.include_hrp())

            if uw_bridge_user is None or\
               in_db and uw_bridge_user.is_new() or\
               not in_db and not uw_bridge_user.is_new():
                self.add_error(
                    "%s Bridge user %s ==> error state in DB %s" %
                    (("update" if in_db else "create"),
                     bridge_user, uw_bridge_user))
                return

            if uw_bridge_user.is_new():
                # created manually in Bridge, now added in DB
                uw_bridge_user.set_no_action()

            if del_user is not None:
                self.merge_user_accounts(del_user, uw_bridge_user)

            self.update_bridge(bridge_user, uw_bridge_user)

        except Exception as ex:
            log_exception(self.logger,
                          "Take_action failed (%s)" % bridge_user,
                          traceback.format_exc())
            self.worker.append_error(
                "Take_action failed %s: %s" % (bridge_user, ex))

    def update_bridge(self, bridge_user, uw_bridge_user):
        uw_bridge_user.set_bridge_id(bridge_user.bridge_id)
        if self.changed_attributes(bridge_user, uw_bridge_user):
            self.logger.info("worker.update %s" % uw_bridge_user)
            self.worker.update_user(uw_bridge_user)

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
