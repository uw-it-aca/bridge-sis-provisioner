from __future__ import unicode_literals
from django.apps import AppConfig
from restclients_core.dao import MockDAO
import os


from django.apps import AppConfig


class BridgeProvisionerConfig(AppConfig):
    name = 'sis_provisioner'
    verbose_name = 'Bridge User Provisioner'

    def ready(self):
        mocks = os.path.join(os.path.dirname(__file__), "resources")
        MockDAO.register_mock_path(mocks)
