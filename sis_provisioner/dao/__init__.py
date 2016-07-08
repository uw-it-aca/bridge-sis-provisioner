from restclients.dao import GWS_DAO


def is_using_file_dao():
    dao = GWS_DAO()._getDAO()
    class_name = dao.__class__.__name__
    return class_name == "File"
