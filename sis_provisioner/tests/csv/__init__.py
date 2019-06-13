from django.test.utils import override_settings
from uw_pws.util import fdao_pws_override
from uw_hrp.util import fdao_hrp_override
from sis_provisioner.tests.account_managers import set_db_records


user_file_name_override = override_settings(
    BRIDGE_IMPORT_USER_FILENAME="users")
