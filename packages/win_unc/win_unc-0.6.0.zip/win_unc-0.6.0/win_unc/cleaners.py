"""
Functions for "cleaning" various pieces needed to make UNC connections. "Cleaning" refers to
removing or changing characters in a string without changing its meaning.
"""


def clean_drive_letter(string):
    """
    A cleaned drive letter is always upper-case, does not have any trailing colons (`:`) or
    backslashes (`\`), and does not have leading or trailing whitespace.
    For example, cleaning "  e:\ " results in "E".
    """
    return string.strip().rstrip(':\\').upper()


def clean_username(string):
    """
    A cleaned Windows username (logon) does not have leading or trailing whitespace.
    For example, cleaning "  username  " results in "username".
    """
    return string.strip()


def clean_unc_path(string):
    """
    A cleaned UNC path does not have trailing backslashes (`\`) nor leading or trailing whitespace.
    For example, cleaning "  \\path\to\folder\  " results in "\\path\to\folder".
    """
    return string.strip().rstrip('\\')
