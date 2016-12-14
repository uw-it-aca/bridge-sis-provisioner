from restclients.models.bridge import BridgeUser
from restclients.bridge.custom_field import new_regid_custom_field


def mock_bridge_user(bridge_id, netid, regid, email, full_name,
                     first_name=None, last_name=None):
    buser = BridgeUser()
    buser.bridge_id = bridge_id
    buser.netid = netid
    buser.full_name = full_name
    buser.first_name = first_name
    buser.last_name = last_name
    buser.email = email
    buser.custom_fields.append(new_regid_custom_field(regid))
    return buser
