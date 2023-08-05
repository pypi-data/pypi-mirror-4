from unittest import TestCase

from win_unc import validators as V


class TestIsValidDriveLetter(TestCase):
    def test_valid(self):
        self.assertTrue(V.is_valid_drive_letter('A'))
        self.assertTrue(V.is_valid_drive_letter('Z'))
        self.assertTrue(V.is_valid_drive_letter('a'))
        self.assertTrue(V.is_valid_drive_letter('z'))

    def test_invalid(self):
        self.assertFalse(V.is_valid_drive_letter(''))
        self.assertFalse(V.is_valid_drive_letter(':'))
        self.assertFalse(V.is_valid_drive_letter('aa'))
        self.assertFalse(V.is_valid_drive_letter('a:'))


class TestIsValidUncPath(TestCase):
    def test_valid(self):
        self.assertTrue(V.is_valid_unc_path(r'\\a'))
        self.assertTrue(V.is_valid_unc_path(r'\\a\b\c'))
        self.assertTrue(V.is_valid_unc_path(r'\\ABC\\'))

    def test_invalid(self):
        self.assertFalse(V.is_valid_unc_path(''))
        self.assertFalse(V.is_valid_unc_path('    '))
        self.assertFalse(V.is_valid_unc_path(r'\\'))
        self.assertFalse(V.is_valid_unc_path(r'  \\a'))
        self.assertFalse(V.is_valid_unc_path(r'\\a  '))
        self.assertFalse(V.is_valid_unc_path(r'\\\a'))
        self.assertFalse(V.is_valid_unc_path(r'C:\path'))
        self.assertFalse(V.is_valid_unc_path(r'\\<a>'))


class TestIsValidUsername(TestCase):
    def test_valid(self):
        self.assertTrue(V.is_valid_username('a'))
        self.assertTrue(V.is_valid_username('abc'))
        self.assertTrue(V.is_valid_username('ABC def'))
        self.assertTrue(V.is_valid_username(".-_ '$"))

    def test_invalid(self):
        self.assertFalse(V.is_valid_username(''))
        self.assertFalse(V.is_valid_username('"abc"'))
        self.assertFalse(V.is_valid_username('/abc'))
        self.assertFalse(V.is_valid_username('  abc'))
        self.assertFalse(V.is_valid_username('abc  '))
