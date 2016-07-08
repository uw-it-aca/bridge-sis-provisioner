from django.test import TestCase
from sis_provisioner.test import FGWS
from sis_provisioner.dao import is_using_file_dao


class TestDao(TestCase):
    def test_is_using_file_dao(self):
        with self.settings(RESTCLIENTS_GWS_DAO_CLASS=FGWS):
            self.assertTrue(is_using_file_dao())
