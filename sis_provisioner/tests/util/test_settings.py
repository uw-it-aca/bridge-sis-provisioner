from django.test import TestCase
from django.conf import settings
from sis_provisioner.util.settings import errors_to_abort_loader


class TestSetting(TestCase):

    def test_default(self):
        with self.settings(ERRORS_TO_ABORT_LOADER=[400]):
            errors = errors_to_abort_loader()
            self.assertEqual(len(errors), 1)
            self.assertEqual(errors[0], 400)
