# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase
from freezegun import freeze_time
from sis_provisioner.tests import fdao_hrp_override, fdao_pws_override
from sis_provisioner.dao import DataFailureException
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
        self.assertIsNotNone(worker.primary_position)
        self.assertEqual(len(worker.other_active_positions), 1)

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
        worker_refs = get_worker_updates(30)
        self.assertEqual(len(worker_refs), 2)

    def test_get_worker_updates_err(self):
        self.assertRaises(DataFailureException,
                          get_worker_updates, 30)
