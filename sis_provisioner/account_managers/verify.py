"""
This class will check the users in DB, if the action on a user record failed
in the last load, re-apply it.
"""

import logging
from sis_provisioner.dao.bridge import get_user_bridge_id
from sis_provisioner.account_managers import fetch_users_from_db


logger = logging.getLogger(__name__)


def set_bridge_ids():
    total = 0
    for uw_bri_user in fetch_users_from_db(logger):
        if not uw_bri_user.has_bridge_id():
            bridge_id = get_user_bridge_id(uw_bri_user)
            if bridge_id > 0:
                uw_bri_user.set_bridge_id(bridge_id)
                logger.info("Set bridge id for %s" % uw_bri_user)
                total = total + 1
        if not uw_bri_user.no_action() and\
                not uw_bri_user.disabled and\
                not uw_bri_user.has_terminate_date():
            uw_bri_user.save_verified(upd_last_visited=False)

    return total
