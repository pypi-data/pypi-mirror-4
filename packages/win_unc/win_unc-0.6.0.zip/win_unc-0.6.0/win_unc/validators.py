from win_unc.internal.utils import take_while
from win_unc.sanitizors import sanitize_username, sanitize_unc_path


def is_valid_drive_letter(string):
    """
    Drive letters are one character in length and between "A" and "Z". Case does not matter.
    """
    return (len(string) == 1
            and string[0].isalpha())


def is_valid_unc_path(string):
    """
    Valid UNC paths are at least three characters long, begin with exactly two backslashes, do not
    start or end with whitepsace, and do not contain certain invalid characters
    (see `sanitize_unc_path`).
    """
    return (len(string) > 2
            and len(take_while(lambda c: c == '\\', string)) == 2
            and string == string.strip()
            and string == sanitize_unc_path(string))


def is_valid_username(string):
    """
    A valid Windows username (logon) is a non-empty string that does not start or end with
    whitespace, and does not contain certain invalid characters (see `sanitize_username`).
    """
    return (len(string) > 0
            and string == string.strip()
            and string == sanitize_username(string))
