import re
from string import capwords
from nameparser import HumanName
from uw_bridge.models import BridgeCustomField


def get_email(person):
    if len(person.email_addresses) == 0:
        return "{0}@uw.edu".format(person.uwnetid)

    email_str = person.email_addresses[0]
    email_s1 = re.sub(" ", "", email_str)
    return re.sub(r"\.$", "", email_s1, flags=re.IGNORECASE)


def get_full_name(person):
    if (len(person.display_name) > 0 and
            not person.display_name.isdigit() and
            not person.display_name.isupper()):
        return person.display_name

    name = HumanName(person.full_name)
    name.capitalize()
    name.string_format = "{first} {last}"
    return str(name)


def normalize_name(name):
    """
    Return a title faced name if the name is not empty
    """
    if name is not None and len(name) > 0:
        return capwords(name)
    return ""


def get_regid(bridge_account):
    cf = bridge_account.get_custom_field(BridgeCustomField.REGID_NAME)
    if cf is not None:
        return cf.value
    return None
