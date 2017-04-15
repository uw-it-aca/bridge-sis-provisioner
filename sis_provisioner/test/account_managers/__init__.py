import logging
from django.test import TestCase
from restclients.exceptions import DataFailureException
from restclients.models.bridge import BridgeUser
from restclients.bridge.custom_field import new_regid_custom_field
from sis_provisioner.account_managers import get_validated_user,\
    _user_left_uw, NO_CHANGE, DISALLOWED, INVALID, LEFT_UW, CHANGED,\
    fetch_users_from_gws
from sis_provisioner.test import fdao_pws_override, fdao_gws_override


logger = logging.getLogger(__name__)


def mock_bridge_user(bridge_id, netid, regid, email, full_name,
                     first_name=None, last_name=None):
    buser = BridgeUser()
    buser.bridge_id = bridge_id
    buser.netid = netid
    buser.full_name = full_name
    buser.first_name = first_name
    buser.last_name = last_name
    buser.email = email
    buser.custom_fields.append(new_regid_custom_field(regid))
    return buser


@fdao_gws_override
@fdao_pws_override
class TestValidUser(TestCase):

    def test_fetch_users_from_gws(self):
        users = fetch_users_from_gws(logger)
        self.assertEqual(len(users), 12)
        self.assertTrue("botgrad" in users)
        self.assertTrue("faculty" in users)
        self.assertTrue("renamed" in users)
        self.assertTrue("much_too_long_much_too_long" in users)
        self.assertTrue("affiemp" in users)

    def test__user_left_uw(self):
        users_in_gws = fetch_users_from_gws(logger)
        self.assertFalse(_user_left_uw(users_in_gws, "faculty"))
        self.assertFalse(_user_left_uw(users_in_gws, "none"))
        self.assertFalse(_user_left_uw(users_in_gws, "retiree"))
        self.assertTrue(_user_left_uw(users_in_gws, "leftuw"))
        self.assertTrue(_user_left_uw(users_in_gws, "invaliduid"))

    def test_get_validated_user(self):
        users_in_gws = fetch_users_from_gws(logger)
        person, validation_status = get_validated_user(
            logger, "botgrad",
            uwregid="10000000000000000000000000000003",
            users_in_gws=users_in_gws)
        self.assertEqual(person.uwnetid, 'botgrad')
        self.assertEqual(validation_status, NO_CHANGE)

        person, validation_status = get_validated_user(
            logger, "changed",
            uwregid="9136CCB8F66711D5BE060004AC494FFE",
            users_in_gws=users_in_gws)
        self.assertEqual(validation_status, CHANGED)

        person, validation_status = get_validated_user(
            logger, 'leftuw',
            uwregid="56229F4D3B504559AF23956737A3CF9D",
            users_in_gws=users_in_gws)
        self.assertEqual(validation_status, CHANGED)

        person, validation_status = get_validated_user(
            logger, 'leftuw',
            users_in_gws=users_in_gws)
        self.assertEqual(validation_status, LEFT_UW)

        person, validation_status = get_validated_user(
            logger, 'leftuw',
            uwregid="B814EFBC6A7C11D5A4AE0004AC494FFE",
            users_in_gws=users_in_gws)
        self.assertEqual(validation_status, LEFT_UW)

        person, validation_status = get_validated_user(
            logger, 'none',
            users_in_gws=users_in_gws)
        self.assertIsNone(person)
        self.assertEqual(validation_status, DISALLOWED)

        person, validation_status = get_validated_user(
            logger, 'changed',
            uwregid="136CCB8F66711D5BE060004AC494FFE",
            users_in_gws=users_in_gws)
        self.assertIsNone(person)
        self.assertEqual(validation_status, INVALID)

        person, validation_status = get_validated_user(
            logger, 'much_too_long_much_too_long',
            uwregid="136CCB8F66711D5BE060004AC494FFE",
            users_in_gws=users_in_gws)
        self.assertIsNone(person)
        self.assertEqual(validation_status, INVALID)

        self.assertRaises(DataFailureException,
                          get_validated_user,
                          logger,
                          'renamed',
                          users_in_gws=users_in_gws)
