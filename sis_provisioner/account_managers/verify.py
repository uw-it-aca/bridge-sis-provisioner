"""
This class will check the users in DB, if the action on a user record failed
in the last load, re-apply it.
"""

import logging
from restclients.exceptions import DataFailureException
from sis_provisioner.dao.bridge import get_bridge_user_object
from sis_provisioner.account_managers import fetch_users_from_db


logger = logging.getLogger(__name__)


def set_bridge_ids():
    total = 0
    set_bridge_id_total = 0

    for uw_bri_user in fetch_users_from_db(logger):

        if uw_bri_user.has_bridge_id() and\
           (uw_bri_user.no_action() or\
            uw_bri_user.disabled or\
            uw_bri_user.has_terminate_date()):
            continue

        try:
            bridge_user = get_bridge_user_object(uw_bri_user)

            if bridge_user is not None:

                if bridge_user.netid != uw_bri_user.netid:
                    logger.error("Bridge and Local Netid not match: %s %s" %
                                 (bridge_user, uw_bri_user))
                    continue

                if not uw_bri_user.has_bridge_id():
                    uw_bri_user.set_bridge_id(bridge_user.bridge_id)
                    logger.info("Set bridge id for %s" % uw_bri_user)
                    set_bridge_id_total = set_bridge_id_total + 1

                uw_bri_user.save_verified(upd_last_visited=False)
                total = total + 1

        except DataFailureException as ex:
            logger.error("GET %s ==> %s" % (uw_bri_user, ex))
            if ex.status == 404:
                logger.info("Not in Bridge, remove local record %s" %
                            uw_bri_user)
                uw_bri_user.delete()

    logger.info("Set bridge ids for %d users" % set_bridge_id_total)
    logger.info("Verified %d users" % total)
    return set_bridge_id_total
