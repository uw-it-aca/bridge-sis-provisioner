# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test.utils import override_settings
from sis_provisioner.tests import (
    fdao_pws_override, fdao_hrp_override, fdao_bridge_override)
from sis_provisioner.tests.account_managers import set_uw_account

user_file_name_override = override_settings(
    BRIDGE_IMPORT_USER_FILENAME="users")


def set_db_records():
    affiemp = set_uw_account("affiemp")

    javerage = set_uw_account("javerage")

    ellen = set_uw_account("ellen")

    staff = set_uw_account("staff")
    staff.set_disable()

    retiree = set_uw_account("retiree")

    tyler = set_uw_account("faculty")

    leftuw = set_uw_account("leftuw")
    leftuw.set_terminate_date()

    testid = set_uw_account("testid")
