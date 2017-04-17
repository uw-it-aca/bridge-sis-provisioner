"""
This class will check the users in DB, if the action on a user record failed
in the last load, re-apply it.
"""

import logging
from restclients.exceptions import DataFailureException
from sis_provisioner.dao.bridge import is_active_user_exist
from sis_provisioner.account_managers import fetch_users_from_db


logger = logging.getLogger(__name__)


def set_bridge_ids():
    total = 0
    set_bridge_id_total = 0

    for uw_bri_user in fetch_users_from_db(logger):
        if uw_bri_user.disabled:
            continue
        try:
            total = total + 1
            active, bridge_user = is_active_user_exist(uw_bri_user.netid)
            if active:
                if not uw_bri_user.has_bridge_id():
                    uw_bri_user.set_bridge_id(bridge_user.bridge_id)
                    logger.info("Set bridge id for %s" % uw_bri_user)
                    set_bridge_id_total = set_bridge_id_total + 1
                else:
                    if bridge_user.bridge_id != uw_bri_user.bridge_id:
                        logger.info("Update BridgeID on local %s by %s",
                                    bridge_user, uw_bri_user)
                        uw_bri_user.set_bridge_id(bridge_user.bridge_id)
                        set_bridge_id_total = set_bridge_id_total + 1
        except DataFailureException as ex:
            logger.error("GET %s ==> %s" % (uw_bri_user, ex))
            if ex.status == 404:
                logger.info("Not in Bridge, remove local record %s" %
                            uw_bri_user)
                uw_bri_user.delete()

    logger.info("Set bridge ids for %d users" % set_bridge_id_total)
    logger.info("Verified %d users" % total)
    return set_bridge_id_total
