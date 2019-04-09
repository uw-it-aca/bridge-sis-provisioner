import re
from string import capwords
from nameparser import HumanName
from uw_bridge.custom_field import new_regid_custom_field
from uw_bridge.models import BridgeUser
from sis_provisioner.dao.bridge import get_regid_from_bridge_user


def account_not_changed(uw_account, person, bridge_account):
    """
    :param uw_account: a valid UwBridgeUser object
    :param person: a valid Person object
    :param bridge_account: a valid BridgeUser object
    :return: True if the attributes have the same values
    """
    return (person.uwnetid == bridge_account.netid and
            get_email(person) == bridge_account.email and
            get_full_name(person) == bridge_account.full_name and
            _normalize_name(person.surname) == bridge_account.last_name and
            _not_changed_regid(person.uwregid, bridge_account))


def get_full_name(person):
    if (len(person.display_name) > 0 and
            not person.display_name.isdigit() and
            not person.display_name.isupper()):
        return person.display_name

    name = HumanName(person.full_name)
    name.capitalize()
    name.string_format = "{first} {last}"
    return str(name)


def get_email(person):
    if len(person.email_addresses) == 0:
        return "{0}@uw.edu".format(person.uwnetid)

    email_str = person.email_addresses[0]
    email_s1 = re.sub(" ", "", email_str)
    return re.sub(r"\.$", "", email_s1, flags=re.IGNORECASE)


def _not_changed_regid(uwregid, bridge_account):
    regid = get_regid_from_bridge_user(bridge_account)
    return (regid is not None and uwregid == regid)


def _normalize_name(name):
    """
    Return a title faced name if the name is not empty
    """
    if name is not None and len(name) > 0:
        return capwords(name)
    return ""


def get_bridge_user_to_add(person):
    """
    :param person: a valid Person object
    :return: a BridgeUser object
    """
    user = BridgeUser(netid=person.uwnetid,
                      email=get_email(person),
                      full_name=get_full_name(person),
                      first_name=_normalize_name(person.first_name),
                      last_name=_normalize_name(person.surname))
    user.custom_fields.append(new_regid_custom_field(person.uwregid))
    return user


def get_bridge_user_to_upd(person, existing_bridge_account):
    """
    :param person: a valid Person object
    :param existing_bridge_account: a valid BridgeUser object
    :return: a BridgeUser object
    """
    user = BridgeUser(bridge_id=existing_bridge_account.bridge_id,
                      netid=person.uwnetid,
                      email=get_email(person),
                      full_name=get_full_name(person),
                      first_name=_normalize_name(person.first_name),
                      last_name=_normalize_name(person.surname))

    if _not_changed_regid(person.uwregid, existing_bridge_account) is False:
        cus_field = new_regid_custom_field(person.uwregid)
        user.custom_fields.append(cus_field)
    return user


def save_bridge_id(uw_account, bridge_id):
    if uw_account.has_bridge_id() is False:
        uw_account.set_bridge_id(bridge_id)
