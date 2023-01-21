# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase
from freezegun import freeze_time
from sis_provisioner.tests import fdao_hrp_override, fdao_pws_override
from sis_provisioner.dao import DataFailureException, changed_since_str
from sis_provisioner.dao.pws import get_person
from sis_provisioner.dao.hrp import get_worker, get_worker_updates


@fdao_hrp_override
@fdao_pws_override
class TestHrpDao(TestCase):

    def test_get_worker(self):
        for netid in ['staff', 'faculty']:
            person = get_person(netid)
            worker = get_worker(person)
            self.assertEqual(worker.netid, netid)

        person = get_person('javerage')
        worker = get_worker(person)
        self.assertEqual(worker.primary_manager_id, "100000001")
        self.assertEqual(len(worker.worker_details), 1)
        positions = worker.worker_details[0]
        self.assertIsNotNone(positions.primary_position)
        self.assertEqual(len(positions.other_active_positions), 1)

        person = get_person('affiemp')
        self.assertIsNone(get_worker(person))

        person = get_person('alumni')
        self.assertIsNone(get_worker(person))

        person = get_person('bill')
        self.assertIsNone(get_worker(person))

        person = get_person('error500')
        self.assertIsNone(get_worker(person))

    @freeze_time("2019-09-01 10:30:00")
    def test_get_worker_updates(self):
        self.assertEqual(changed_since_str(
            30, iso=True), "2019-09-01T03:00:00.000000-0700")
        persons = get_worker_updates(30)
        self.assertEqual(len(persons), 2)
        self.assertEqual(persons[0].primary_manager_id, "100000001")
        self.assertFalse(persons[1].is_active)

    def test_get_worker_updates_err(self):
        self.assertRaises(DataFailureException,
                          get_worker_updates, 30)
