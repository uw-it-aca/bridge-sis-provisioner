from uw_bridge.custom_field import new_regid_custom_field
from uw_bridge.models import BridgeUser


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
    user.custom_fields.append(new_regid_custom_field(uwregid))
    return user
