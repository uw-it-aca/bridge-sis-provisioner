from datetime import timedelta
from sis_provisioner.models import BridgeUser, get_now


FGWS = 'restclients.dao_implementation.gws.File'
FPWS = 'restclients.dao_implementation.pws.File'
FHRP = 'restclients.dao_implementation.hrpws.File'


def set_pass_terminate_date(uwnetid):
    user = BridgeUser.objects.get(netid=uwnetid)
    if user:
        user.terminate_date = get_now() - timedelta(days=16)
        user.save()
