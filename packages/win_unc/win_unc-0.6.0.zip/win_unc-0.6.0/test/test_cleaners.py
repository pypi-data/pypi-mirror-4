from unittest import TestCase

from win_unc import cleaners as C


class TestCleaners(TestCase):
    def test_clean_drive_letter(self):
        self.assertEqual(C.clean_drive_letter('A'), 'A')
        self.assertEqual(C.clean_drive_letter('A:'), 'A')
        self.assertEqual(C.clean_drive_letter('A:\\'), 'A')
        self.assertEqual(C.clean_drive_letter('a'), 'A')
        self.assertEqual(C.clean_drive_letter('a:\\'), 'A')

    def test_clean_username(self):
        self.assertEqual(C.clean_username('username'), 'username')
        self.assertEqual(C.clean_username('userNAME'), 'userNAME')
        self.assertEqual(C.clean_username('  user'), 'user')
        self.assertEqual(C.clean_username('user  '), 'user')
        self.assertEqual(C.clean_username(' user '), 'user')

    def test_clean_unc_path(self):
        self.assertEqual(C.clean_unc_path(r'\\path'), r'\\path')
        self.assertEqual(C.clean_unc_path(r'\\path\B'), r'\\path\B')
        self.assertEqual(C.clean_unc_path(r'\\path\IPC$'), r'\\path\IPC$')
        self.assertEqual(C.clean_unc_path(r'\\path\\'), r'\\path')
        self.assertEqual(C.clean_unc_path(r'  \\path'), r'\\path')
        self.assertEqual(C.clean_unc_path(r'\\path  '), r'\\path')
        self.assertEqual(C.clean_unc_path(r' \\path '), r'\\path')
