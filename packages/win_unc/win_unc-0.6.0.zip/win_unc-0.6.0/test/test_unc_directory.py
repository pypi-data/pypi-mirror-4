from unittest import TestCase

from win_unc.errors import InvalidUncPathError
from win_unc.unc_directory import UncDirectory, get_unc_directory_from_string, is_unc_directory_string
from win_unc.unc_credentials import UncCredentials


class TestUncDirectory(TestCase):
    def test_init_with_invalid_path(self):
        self.assertRaises(InvalidUncPathError, UncDirectory, '')
        self.assertRaises(InvalidUncPathError, UncDirectory, 'abc')
        self.assertRaises(InvalidUncPathError, UncDirectory, r'\\\abc')
        self.assertRaises(InvalidUncPathError, UncDirectory, r'C:\not-unc\path')

    def test_init_with_cloning(self):
        unc = UncDirectory(UncDirectory(r'\\path'))
        self.assertEqual(unc.get_path(), r'\\path')
        self.assertIsNone(unc.get_username())
        self.assertIsNone(unc.get_password())

        creds = UncCredentials('user')
        unc = UncDirectory(UncDirectory(r'\\path', creds))
        self.assertEqual(unc.get_path(), r'\\path')
        self.assertEqual(unc.get_username(), 'user')
        self.assertIsNone(unc.get_password())

        creds = UncCredentials(None, 'pass')
        unc = UncDirectory(UncDirectory(r'\\path', creds))
        self.assertEqual(unc.get_path(), r'\\path')
        self.assertIsNone(unc.get_username())
        self.assertEqual(unc.get_password(), 'pass')

        creds = UncCredentials('user', 'pass')
        unc = UncDirectory(UncDirectory(r'\\path', creds))
        self.assertEqual(unc.get_path(), r'\\path')
        self.assertEqual(unc.get_username(), 'user')
        self.assertEqual(unc.get_password(), 'pass')

    def test_eq(self):
        self.assertEqual(UncDirectory(r'\\path'), UncDirectory(r'\\path'))
        self.assertEqual(UncDirectory(r'\\path'), UncDirectory(r'\\PATH'))

        creds = UncCredentials('user')
        self.assertEqual(UncDirectory(r'\\path', creds), UncDirectory(r'\\path', creds))
        self.assertEqual(UncDirectory(r'\\path', creds), UncDirectory(r'\\PATH', creds))

        creds = UncCredentials('user', 'pass')
        self.assertEqual(UncDirectory(r'\\path', creds), UncDirectory(r'\\path', creds))
        self.assertEqual(UncDirectory(r'\\path', creds), UncDirectory(r'\\PATH', creds))

    def test_ne(self):
        creds1 = UncCredentials('user')
        creds2 = UncCredentials('USER')
        self.assertNotEqual(UncDirectory(r'\\path', creds1), UncDirectory(r'\\path', creds2))

        creds1 = UncCredentials('user', 'pass')
        creds2 = UncCredentials('user', 'PASS')
        self.assertNotEqual(UncDirectory(r'\\path', creds1), UncDirectory(r'\\path', creds2))

        self.assertNotEqual(UncDirectory(r'\\path'), 'somestring')

    def test_get_normalized_path(self):
        self.assertEqual(UncDirectory(r'\\abc').get_normalized_path(), r'\\abc')
        self.assertEqual(UncDirectory(r'\\ABC').get_normalized_path(), r'\\abc')
        self.assertEqual(UncDirectory(r'\\abc\def').get_normalized_path(), r'\\abc\def')
        self.assertEqual(UncDirectory(r'\\abc\DEF').get_normalized_path(), r'\\abc\def')
        self.assertEqual(UncDirectory(r'\\abc\def\\').get_normalized_path(), r'\\abc\def')
        self.assertEqual(UncDirectory(r'\\abc\IPC$').get_normalized_path(), r'\\abc')
        self.assertEqual(UncDirectory(r'\\abc\ipc$').get_normalized_path(), r'\\abc')

    def test_get_auth_path(self):
        self.assertEqual(UncDirectory(r'\\path').get_auth_path(), r'\\path')

        creds = UncCredentials('user')
        self.assertEqual(UncDirectory(r'\\path', creds).get_auth_path(), r'user@\\path')

        creds = UncCredentials('user', 'pass')
        self.assertEqual(UncDirectory(r'\\path', creds).get_auth_path(), r'user:pass@\\path')


class TestParsing(TestCase):
    def test_is_unc_directory_string(self):
        self.assertFalse(is_unc_directory_string(''))
        self.assertFalse(is_unc_directory_string('abc'))
        self.assertFalse(is_unc_directory_string('\\'))
        self.assertFalse(is_unc_directory_string('\\\\'))
        self.assertFalse(is_unc_directory_string('@\\'))
        self.assertFalse(is_unc_directory_string('@\\\\'))
        self.assertFalse(is_unc_directory_string('abc@\\\\'))

        self.assertTrue(is_unc_directory_string(r'\\abc'))
        self.assertTrue(is_unc_directory_string(r'\\abc\def'))
        self.assertTrue(is_unc_directory_string(r'@\\abc\def'))
        self.assertTrue(is_unc_directory_string(r'user@\\abc\def'))
        self.assertTrue(is_unc_directory_string(r'user:pass@\\abc\def'))
        self.assertTrue(is_unc_directory_string(r':pass@\\abc\def'))

    def test_get_unc_directory_from_string(self):
        self.assertEqual(get_unc_directory_from_string(r'\\path'), UncDirectory(r'\\path'))
        self.assertEqual(get_unc_directory_from_string(r'\\path\sub'),
                         UncDirectory(r'\\path\sub'))

        creds = UncCredentials('user')
        self.assertEqual(get_unc_directory_from_string(r'user@\\path'),
                         UncDirectory(r'\\path', creds))

        creds = UncCredentials(None, 'pass')
        self.assertEqual(get_unc_directory_from_string(r':pass@\\path'),
                         UncDirectory(r'\\path', creds))

        creds = UncCredentials(None, r':@\\')
        self.assertEqual(get_unc_directory_from_string(r'::@\\@\\path'),
                         UncDirectory(r'\\path', creds))

        creds = UncCredentials('user', 'pass')
        self.assertEqual(get_unc_directory_from_string(r'user:pass@\\path'),
                         UncDirectory(r'\\path', creds))

        creds = UncCredentials('user', r':@\\')
        self.assertEqual(get_unc_directory_from_string(r'user::@\\@\\path'),
                         UncDirectory(r'\\path', creds))
