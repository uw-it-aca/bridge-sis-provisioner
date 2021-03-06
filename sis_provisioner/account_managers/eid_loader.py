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
    updated = 0
    for uw_acc in get_all_uw_accounts():
        uwnetid = uw_acc.netid
        person = get_person(uwnetid)
        if (person is not None and person.is_employee and
                person.is_test_entity is False):
            total += 1
            if (uw_acc.employee_id is None or
                    uw_acc.employee_id != person.employee_id):
                uw_acc.set_employee_id(person.employee_id)
                uw_acc.save()
                updated += 1
    msg = "Updated employee_ids for {0} out of {1} users".format(
        updated, total)
    logger.info(msg)
    return msg
