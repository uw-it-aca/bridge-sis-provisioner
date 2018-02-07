from uw_pws.dao import PWS_DAO


def is_using_file_dao():
    return PWS_DAO().get_implementation().is_mock()
