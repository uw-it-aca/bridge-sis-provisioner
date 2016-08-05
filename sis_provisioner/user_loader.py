import logging
import traceback
import json
from restclients.exceptions import DataFailureException
from sis_provisioner.dao.gws import get_uw_members
from sis_provisioner.dao.user import create_user
from sis_provisioner.util.log import log_exception
from sis_provisioner.util.list_helper import get_item_counts_dict
from sis_provisioner.loader import AbsLoader


logger = logging.getLogger(__name__)


class UserLoader(AbsLoader):

    def __init__(self, include_hrp=False):
        self.include_hrp_data = include_hrp

    def init_set(self):
        self.total_count = 0
        # a list of BridgeUser objects
        self.users_to_add = []
        self.users_changed_netid = []
        self.users_changed_regid = []
        self.emp_app_totals = []
        # a list of netids
        self.users_to_del = []

    def fetch_all(self):
        self.init_set()
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
                user_add, deletes = create_user(
                    uwnetid, include_hrp=self.include_hrp_data)

                if user_add is not None and\
                        not user_add.no_action():

                    if self.include_hrp() and user_add.is_employee:
                        self.emp_app_totals.append(
                            user_add.get_total_emp_apps())

                    if user_add.netid_changed():
                        self.users_changed_netid.append(user_add)
                    elif user_add.regid_changed():
                        self.users_changed_regid.append(user_add)
                    else:
                        self.users_to_add.append(user_add)

                if deletes is not None and len(deletes) > 0:
                    for netid in deletes:
                        self.users_to_del.append(netid)

            except Exception as ex:
                log_exception(logger,
                              "Failed to create user (%s)" % uwnetid,
                              traceback.format_exc())
                continue
        self.log_status()

    def log_status(self):
        logger.info("Finish loading %d users." % self.get_total_count())
        logger.info("%d users normal import." % self.get_add_count())
        logger.info("%d users changed netid." % self.get_netid_changed_count())
        logger.info("%d users changed regid." % self.get_regid_changed_count())
        logger.info("%d users to delete." % self.get_delete_count())
        if self.include_hrp():
            counts_dict = get_item_counts_dict(self.emp_app_totals)
            logger.info("appointments counts: %s" % json.dumps(counts_dict))

    def include_hrp(self):
        return self.include_hrp_data

    def get_total_count(self):
        return self.total_count

    def get_add_count(self):
        return len(self.users_to_add)

    def get_netid_changed_count(self):
        return len(self.users_changed_netid)

    def get_regid_changed_count(self):
        return len(self.users_changed_regid)

    def get_delete_count(self):
        return len(self.users_to_del)

    def get_users_to_add(self):
        return self.users_to_add

    def get_users_to_delete(self):
        return self.users_to_del

    def get_users_netid_changed(self):
        return self.users_changed_netid

    def get_users_regid_changed(self):
        return self.users_changed_regid
