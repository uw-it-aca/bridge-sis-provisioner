from uw_bridge.custom_fields import CustomFields
from uw_bridge.models import BridgeCustomField, BridgeUser


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
        new_regid_custom_field(uwregid)
    return user


def new_regid_custom_field(uwregid):
    return CustomFields().new_custom_field(BridgeCustomField.REGID_NAME,
                                           uwregid)


def get_regid(bridge_account):
    cf = bridge_account.get_custom_field(BridgeCustomField.REGID_NAME)
    if cf is not None:
        return cf.value
    return None
