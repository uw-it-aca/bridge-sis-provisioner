# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase
from uw_bridge.models import BridgeCustomField
from sis_provisioner.models.work_positions import WORK_POSITION_FIELDS


class TestBridgeFields(TestCase):

    def test_WORK_POSITION_FIELDS(self):
        self.assertEqual(len(WORK_POSITION_FIELDS[0]), 7)
        self.assertEqual(WORK_POSITION_FIELDS[0][0],
                         BridgeCustomField.POS1_BUDGET_CODE)
        self.assertEqual(WORK_POSITION_FIELDS[0][6],
                         BridgeCustomField.POS1_UNIT_CODE)
        self.assertEqual(len(WORK_POSITION_FIELDS[1]), 7)
        self.assertEqual(WORK_POSITION_FIELDS[1][0],
                         BridgeCustomField.POS2_BUDGET_CODE)
        self.assertEqual(WORK_POSITION_FIELDS[1][6],
                         BridgeCustomField.POS2_UNIT_CODE)
