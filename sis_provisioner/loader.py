from abc import ABCMeta, abstractmethod


class AbsLoader:
    __metaclass__ = ABCMeta

    @abstractmethod
    def fetch_all(self): pass

    @abstractmethod
    def include_hrp(self):
        return self.include_hrp_data

    @abstractmethod
    def get_total_count(self): pass

    def get_add_count(self):
        return 0

    def get_netid_changed_count(self):
        return 0

    def get_regid_changed_count(self):
        return 0

    def get_delete_count(self):
        return 0

    def get_users_to_add(self):
        return []

    def get_users_to_delete(self):
        return []

    def get_users_netid_changed(self):
        return []

    def get_users_regid_changed(self):
        return []
