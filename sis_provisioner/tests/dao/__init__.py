# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from uw_bridge.custom_fields import CustomFields
from uw_bridge.models import BridgeCustomField, BridgeUser
from uw_bridge import Bridge

base_bridge = Bridge()


def new_custom_field(name, value):
    return CustomFields(base_bridge).new_custom_field(name, value)


def get_mock_bridge_user(bridge_id,
                         uwnetid, email,
                         display_name,
                         first_name,
                         surname,
                         uwregid):
    user = BridgeUser(bridge_id=bridge_id,
                      netid=uwnetid,
                      email=email,
                      full_name=display_name,
                      first_name=first_name,
                      last_name=surname)
    user.custom_fields[BridgeCustomField.REGID_NAME] = \
        new_custom_field(BridgeCustomField.REGID_NAME, uwregid)
    return user
