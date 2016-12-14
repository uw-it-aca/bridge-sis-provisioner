from sis_provisioner.dao.pws import get_person
from sis_provisioner.dao.user import normalize_email, normalize_name
from sis_provisioner.models import UwBridgeUser, get_now
from sis_provisioner.test import fdao_pws_override


@fdao_pws_override
def mock_uw_bridge_user(uwnetid):
    person = get_person(uwnetid)
    buser = UwBridgeUser()
    buser.netid = person.uwnetid
    buser.regid = person.uwregid
    buser.email = normalize_email(person.email1)
    buser.display_name = person.display_name
    buser.first_name = normalize_name(person.first_name)
    buser.last_name = normalize_name(person.surname)
    buser.is_alum = person.is_alum
    buser.is_employee = person.is_employee
    buser.is_faculty = person.is_faculty
    buser.is_staff = person.is_staff
    buser.is_student = person.is_student
    buser.last_visited_at = get_now()
    return buser, person
