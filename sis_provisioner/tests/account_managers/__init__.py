from sis_provisioner.models import UwAccount, get_now
from sis_provisioner.tests.dao import new_custom_field


def set_uw_account(uwnetid):
    return UwAccount.objects.create(netid=uwnetid,
                                    last_updated=get_now())


def set_db_records():
    javerage = set_uw_account("javerage")
    javerage.set_ids(195, "123456789")

    ellen = set_uw_account("ellen")
    ellen.set_ids(194, "000000006")

    staff = set_uw_account("staff")
    staff.set_disable()
    staff.set_ids(196, "100000001")

    retiree = set_uw_account("retiree")
    retiree.set_ids(204, "000000006")

    tyler = set_uw_account("tyler")
    tyler.set_ids(198, "000000005")

    leftuw = set_uw_account("leftuw")
    leftuw.set_ids(200, None)

    testid = set_uw_account("testid")


def set_db_err_records():
    error500 = set_uw_account("error500")
    error500.set_ids(250, None)

    none = set_uw_account("not_in_pws")
