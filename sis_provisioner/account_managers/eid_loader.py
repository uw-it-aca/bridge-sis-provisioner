"""
This function udpate the employee_id of the user accounts in DB
"""

import logging
import traceback
from sis_provisioner.dao.pws import get_person
from sis_provisioner.dao.uw_account import get_all_uw_accounts


logger = logging.getLogger(__name__)


def load():
    total = 0
    for uw_acc in get_all_uw_accounts():
        uwnetid = uw_acc.netid
        person = get_person(uwnetid)
        if person is None:
            continue
        if person.is_employee:
            uw_acc.set_employee_id(person.employee_id)
            total += 1
    logger.info("Validated employee_ids of {0} users".format(total))
    return total
