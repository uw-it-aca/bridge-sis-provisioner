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
from sis_provisioner.dao.bridge import get_regid_from_bridge_user,\
    is_active_user_exist
from sis_provisioner.models import UwBridgeUser
from sis_provisioner.util.log import log_exception
from sis_provisioner.account_managers import get_validated_user,\
    fetch_users_from_bridge, INVALID, VALID, CHANGED
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
            self.logger.debug("process Bridge user %s", bridge_user)
            uwnetid = bridge_user.netid
            uwregid = get_regid_from_bridge_user(bridge_user)
            try:
                person, validation_status = get_validated_user(
                    logger,
                    uwnetid,
                    uwregid=uwregid,
                    users_in_gws=self.get_users_in_gws())
            except DataFailureException as ex:
                self.worker.append_error(
                    "Validate user %s ==> %s" % (bridge_user, ex))
                continue

            if validation_status == CHANGED:
                exists2, kp_user = is_active_user_exist(person.uwnetid)
                if exists2 and kp_user is not None and\
                   bridge_user.bridge_id != kp_user.bridge_id:
                    # There is another account in Bridge
                    # match to the up-to-date netid, merge them!
                    self.merge_user_accounts(bridge_user, kp_user)
                    continue
                    # If local record with bridge_user.netid exists
                    # it will be deleted by UserUpdater

            # find the DB record(s) that match with the bridge_user
            uw_bri_users = get_users_from_db(bridge_user.bridge_id,
                                             uwnetid,
                                             uwregid)
            in_db = len(uw_bri_users) > 0

            if person is not None and validation_status >= VALID:
                logger.info("Bridge user %s matched person (%s, %s)",
                            bridge_user, person.uwnetid, person.uwregid)
                self.take_action(person, bridge_user, in_db)
                continue

            for user in uw_bri_users:
                if (uwregid is None or uwregid == user.regid) and\
                   uwnetid == user.netid:
                    # only the matched record can be terminated
                    user.set_bridge_id(bridge_user.bridge_id)
                    self.terminate(user, validation_status)
                else:
                    self.add_error(
                        "Bridge user %s not match local record %s" %
                        (bridge_user, user))

    def take_action(self, person, bridge_user, in_db=False):
        """
        Add the Bridge user (not in DB yet) into local DB
        @param person must be a valid object
        """
        try:
            uw_bridge_user, del_user = save_user(
                person, include_hrp=self.include_hrp())
        except Exception as ex:
            log_exception(self.logger,
                          "Save user %s " % bridge_user,
                          traceback.format_exc())
            self.worker.append_error(
                "Save user in DB %s ==> %s" % (bridge_user, ex))
            return

        if uw_bridge_user is None:
            self.add_error(
                "%s Bridge user %s in DB ==> return None" %
                (("Update" if in_db else "Create"), bridge_user))
            return

        if del_user is not None:
            # deleted from local DB as result of a merge
            if del_user.has_bridge_id() and\
               del_user.bridge_id != bridge_user.bridge_id:
                self.merge_user_accounts(del_user, uw_bridge_user)
            else:
                if del_user.netid == bridge_user.netid:
                    self.logger.info("Bridge user %s match deleted user %s",
                                     bridge_user, del_user)
                    self.apply_change_to_bridge(uw_bridge_user)
                    return

        self.update_bridge(bridge_user, uw_bridge_user)

    def update_bridge(self, bridge_user, uw_bridge_user):
        if not self.accounts_match(bridge_user, uw_bridge_user):
            self.apply_change_to_bridge(uw_bridge_user)
            return

        need_to_update, user = self.has_updates(bridge_user, uw_bridge_user)
        if need_to_update:
            self.logger.info("worker.update %s to Bridge user %s",
                             uw_bridge_user, bridge_user)
            self.apply_change_to_bridge(user)

    def accounts_match(self, bridge_user, uw_bridge_user):
        """
        Check if the up-to-date account matches bridge_user
        """
        exists, buser = is_active_user_exist(uw_bridge_user.netid)
        if exists and buser is not None:
            uw_bridge_user.set_bridge_id(buser.bridge_id)

            if bridge_user.bridge_id != buser.bridge_id:
                # this user has another account in Bridge
                self.logger.info("Merge Bridge user %s to %s in Bridge",
                                 bridge_user, uw_bridge_user)
                self.merge_user_accounts(bridge_user, uw_bridge_user)
                return False
            return True

        if not exists and buser is None:
            # uw_bridge_user.netid not exist in Bridge
            # bridge_user.netid must have changed
            uw_bridge_user.set_bridge_id(bridge_user.bridge_id)
            return True

        # exists another terminated account, unable to apply change now
        self.add_error("Bridge user % not match local %s, check!" %
                       (bridge_user, uw_bridge_user))
        return False

    def has_updates(self, bridge_user, uw_bridge_user):
        if uw_bridge_user.is_new():
            uw_bridge_user.set_action_update()

        if bridge_user.netid == uw_bridge_user.prev_netid:
            self.logger.info("Bridge %s == match prev_netid in %s",
                             bridge_user, uw_bridge_user)
            return True, uw_bridge_user

        if bridge_user.netid != uw_bridge_user.netid:
            self.logger.info("Bridge %s == changed netid ==> %s",
                             bridge_user, uw_bridge_user)
            uw_bridge_user.set_prev_netid(bridge_user.netid)
            return True, uw_bridge_user

        regid = get_regid_from_bridge_user(bridge_user)
        if regid != uw_bridge_user.regid:
            self.logger.info("Bridge %s == changed regid ==> %s",
                             bridge_user, uw_bridge_user)
            if not uw_bridge_user.regid_changed():
                uw_bridge_user.set_action_regid_changed()
            return True, uw_bridge_user

        # current attributes 12/10/2016.
        if bridge_user.full_name != uw_bridge_user.get_display_name() or\
           bridge_user.email != uw_bridge_user.get_email():
            uw_bridge_user.set_action_update()
            return True, uw_bridge_user

        self.logger.info(
            "Verified Bridge user %s with %s ==> No change!",
            bridge_user, uw_bridge_user)
        uw_bridge_user.set_no_action()
        return False, uw_bridge_user
