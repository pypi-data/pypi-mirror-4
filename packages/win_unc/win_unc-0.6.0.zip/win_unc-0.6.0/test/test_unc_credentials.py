from unittest import TestCase

from win_unc.errors import InvalidUsernameError
from win_unc.unc_credentials import UncCredentials, get_creds_from_string


class TestUncCredentials(TestCase):
    def test_cloning(self):
        creds = UncCredentials(UncCredentials())
        self.assertIsNone(creds.get_username())
        self.assertIsNone(creds.get_password())

        creds = UncCredentials(UncCredentials('user', None))
        self.assertEqual(creds.get_username(), 'user')
        self.assertIsNone(creds.get_password())

        creds = UncCredentials(UncCredentials(None, 'pass'))
        self.assertIsNone(creds.get_username())
        self.assertEqual(creds.get_password(), 'pass')

        creds = UncCredentials(UncCredentials('user', 'pass'))
        self.assertEqual(creds.get_username(), 'user')
        self.assertEqual(creds.get_password(), 'pass')

    def test_invalid(self):
        self.assertRaises(InvalidUsernameError, UncCredentials, '"user"')
        self.assertRaises(InvalidUsernameError, UncCredentials, '>user')

    def test_get_auth_string(self):
        self.assertEqual(UncCredentials(None, None).get_auth_string(), '')
        self.assertEqual(UncCredentials(None, '').get_auth_string(), ':')

        self.assertEqual(UncCredentials('user', None).get_auth_string(), 'user')
        self.assertEqual(UncCredentials('user', '').get_auth_string(), 'user:')

        self.assertEqual(UncCredentials(None, 'pass').get_auth_string(), ':pass')
        self.assertEqual(UncCredentials('user', ':').get_auth_string(), 'user::')
        self.assertEqual(UncCredentials('user', 'pass').get_auth_string(), 'user:pass')

    def test_eq(self):
        self.assertEqual(UncCredentials(), UncCredentials())
        self.assertEqual(UncCredentials('user', None), UncCredentials('user', None))
        self.assertEqual(UncCredentials(None, 'pass'), UncCredentials(None, 'pass'))
        self.assertEqual(UncCredentials('user', 'pass'), UncCredentials('user', 'pass'))

    def test_ne(self):
        self.assertNotEqual(UncCredentials(), UncCredentials('user'))
        self.assertNotEqual(UncCredentials('user'), UncCredentials('USER'))
        self.assertNotEqual(UncCredentials(None, 'pass'), UncCredentials(None, 'USER'))
        self.assertNotEqual(UncCredentials(), 'somestring')
        self.assertNotEqual(UncCredentials(), 10)


class TestUncParsingFunctions(TestCase):
    def test_get_creds_from_string(self):
        self.assertEqual(get_creds_from_string(''), UncCredentials(None, None))
        self.assertEqual(get_creds_from_string('user'), UncCredentials('user', None))
        self.assertEqual(get_creds_from_string('user'), UncCredentials('user', None))

        self.assertEqual(get_creds_from_string(':""'), UncCredentials(None, '""'))
        self.assertEqual(get_creds_from_string('::'), UncCredentials(None, ':'))
        self.assertEqual(get_creds_from_string(':pass'), UncCredentials(None, 'pass'))

        self.assertEqual(get_creds_from_string('user:'), UncCredentials('user', ''))
        self.assertEqual(get_creds_from_string('user:pass'), UncCredentials('user', 'pass'))
        self.assertEqual(get_creds_from_string('user::'), UncCredentials('user', ':'))
