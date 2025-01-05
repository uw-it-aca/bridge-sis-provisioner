# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
This function udpate the employee_id of the user accounts in DB
"""

import logging
import traceback
from sis_provisioner.dao.pws import get_person
from sis_provisioner.dao.uw_account import get_all_uw_accounts
from sis_provisioner.util.log import log_exception


logger = logging.getLogger(__name__)


def load():
    total = 0
    updated = 0
    for uw_acc in get_all_uw_accounts():
        uwnetid = uw_acc.netid
        try:
            person = get_person(uwnetid)
            if person and person.employee_id is not None:
                total += 1
                if (uw_acc.employee_id is None or
                        uw_acc.employee_id != person.employee_id):
                    uw_acc.set_employee_id(person.employee_id)
                    uw_acc.save()
                    updated += 1
        except Exception:
            log_exception(
                logger,
                "Udpate the employee_id on {0} ".format(uwnetid),
                traceback.format_exc(chain=False))

    msg = "Updated employee_ids for {0} out of {1} users".format(
        updated, total)
    logger.info(msg)
    return msg
