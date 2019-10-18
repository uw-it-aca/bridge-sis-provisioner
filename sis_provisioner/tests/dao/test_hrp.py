from django.test import TestCase
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

    def test_get_worker_updates(self):
        worker_refs = get_worker_updates("2019")
        self.assertEqual(len(worker_refs), 2)
        self.assertRaises(DataFailureException,
                          get_worker_updates, "201909")
