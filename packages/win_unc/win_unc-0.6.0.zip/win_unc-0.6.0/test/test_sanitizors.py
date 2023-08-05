from unittest import TestCase

from win_unc import sanitizors as S


class TestSanitizors(TestCase):
    def test_sanitize_for_shell(self):
        self.assertEqual(S.sanitize_for_shell(''), '')
        self.assertEqual(S.sanitize_for_shell('abcABC'), 'abcABC')
        self.assertEqual(S.sanitize_for_shell('"'), r'\"')
        self.assertEqual(S.sanitize_for_shell('abc"""'), r'abc\"\"\"')

    def test_sanitize_username(self):
        self.assertEqual(S.sanitize_username(''), '')
        self.assertEqual(S.sanitize_username('abcABC'), 'abcABC')
        self.assertEqual(S.sanitize_username(r'"/[]:;|=,+*?<>'), '')
        self.assertEqual(S.sanitize_username(r'"/[]:;|=,+*?<>'), '')
        self.assertEqual(S.sanitize_username('\0'), '')

    def test_sanitize_path(self):
        self.assertEqual(S.sanitize_unc_path(''), '')
        self.assertEqual(S.sanitize_unc_path('abcABC'), 'abcABC')
        self.assertEqual(S.sanitize_unc_path(r'<>"/|?*'), '')
        self.assertEqual(S.sanitize_unc_path('\0\1\2\3\4\30\31'), '')

        self.assertEqual(S.sanitize_path(r'C:\a valid\folder'), r'C:\a valid\folder')
        self.assertEqual(S.sanitize_path(r':\\'), r':\\')

    def test_sanitize_unc_path(self):
        self.assertEqual(S.sanitize_unc_path(''), '')
        self.assertEqual(S.sanitize_unc_path('abcABC'), 'abcABC')
        self.assertEqual(S.sanitize_unc_path(r'<>"/|?*'), '')
        self.assertEqual(S.sanitize_unc_path('\0\1\2\3\4\30\31'), '')

        self.assertEqual(S.sanitize_unc_path(r'C\a valid\folder'), r'C\a valid\folder')
        self.assertEqual(S.sanitize_unc_path(r':\\'), r'\\')

    def test_sanitize_file_name(self):
        self.assertEqual(S.sanitize_unc_path(''), '')
        self.assertEqual(S.sanitize_unc_path('abcABC'), 'abcABC')
        self.assertEqual(S.sanitize_unc_path(r'<>"/|?*'), '')
        self.assertEqual(S.sanitize_unc_path('\0\1\2\3\4\30\31'), '')

        self.assertEqual(S.sanitize_file_name(r'C:\a valid\folder'), r'Ca validfolder')
        self.assertEqual(S.sanitize_file_name(r':\\'), r'')
