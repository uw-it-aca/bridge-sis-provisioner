from restclients_core.exceptions import DataFailureException, InvalidNetID
from uw_pws import DAO as PWS_DAO


def is_using_file_dao():
    return SWS_DAO.get_implementation().is_mock()
