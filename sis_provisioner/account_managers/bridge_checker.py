"""
This class will load all the existing users in bridge,
validate against gws uw_member group and pws person,
and update their database records and the bridge
accounts via the given worker.
"""

import logging
from sis_provisioner.dao.user import get_user_by_netid, get_user_by_regid
from sis_provisioner.models import UwBridgeUser
from sis_provisioner.account_managers import get_validated_user,\
    fetch_users_from_bridge, get_regid_from_bridge_user
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
            person, validation_status = get_validated_user(logger,
                                                           uwnetid,
                                                           uwregid=uwregid,
                                                           check_gws=True)
            try:
                uw_bri_user = get_user_by_netid(uwnetid)
                if uw_bri_user is None:
                    uw_bri_user = get_user_by_regid(uwregid)

                if person is None:
                    self.terminate(uw_bri_user, validation_status)
                else:
                    self.take_action(person, validation_status)

            except UwBridgeUser.DoesNotExist:
                # account created directly in Bridge, just log it.
                # don't touch it.
                err_msg = "Bridge user %s is unknown (not in DB)" % bridge_user
                logger.error(err_msg)
                self.worker.append_error(err_msg)
