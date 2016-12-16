from django.test.utils import override_settings
from restclients.test import fdao_gws_override, fdao_bridge_override,\
    fdao_hrp_override, fdao_pws_override


user_file_name_override = override_settings(
    BRIDGE_IMPORT_USER_FILENAME="users")
