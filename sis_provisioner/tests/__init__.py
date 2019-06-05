from django.test.utils import override_settings
from uw_gws.utilities import fdao_gws_override
from uw_pws.util import fdao_pws_override
from uw_hrp.util import fdao_hrp_override
from uw_bridge.util import fdao_bridge_override


user_file_name_override = override_settings(
    BRIDGE_IMPORT_USER_FILENAME="users")
