from sis_provisioner.models import UwAccount, get_now


def set_uw_account(uwnetid):
    return UwAccount.objects.create(netid=uwnetid,
                                    last_updated=get_now())


def set_db_records():
    javerage = set_uw_account("javerage")
    javerage.set_bridge_id(195)

    ellen = set_uw_account("ellen")
    ellen.set_bridge_id(194)

    staff = set_uw_account("staff")
    staff.set_bridge_id(196)
    staff.disabled = True

    retiree = set_uw_account("retiree")
    retiree.set_bridge_id(204)

    tyler = set_uw_account("tyler")
    tyler.set_bridge_id(198)

    leftuw = set_uw_account("leftuw")
    leftuw.set_bridge_id(200)