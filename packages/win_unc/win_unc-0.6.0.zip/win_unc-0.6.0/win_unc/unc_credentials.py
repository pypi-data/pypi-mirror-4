"""
Class and functions for dealing with credentials in UNC connections on Windows.
"""

from win_unc.errors import InvalidUsernameError
from win_unc.cleaners import clean_username
from win_unc.validators import is_valid_username


class UncCredentials(object):
    """
    Represents a set of credentials to be used with a UNC connection. Credentials include a
    username and a password.
    """

    def __init__(self, username=None, password=None):
        """
        Returns a new `UncCredentials` object. Both `username` and `password` are optional.
        If neither are provided, the new object will mean that credentials are unnecessary.
        `username` must be a string representing a Windows username (logon). Windows usernames
                   may include a domain prefix (i.e. "domain\username"). If `username` cannot be
                   construed as a valid Windows username, then this will raise an
                   `InvalidUsernameError`.
                   Note: UNC connections that require authentication will use the username of the
                         currently logged in Windows user unless specifically provided another
                         username.
                   Note: Providing `None` and `''` (the empty string) have very different meanings.
                         Usernames cannot be empty.
        `password` must be a string representing a password.
                   Note: Providing `None` and `''` (the empty string) have very different meanings.
                   The empty string is a meaningful, legitimate password.

        If only the first positional argument is provided and it is already an instance of the
        `UncCredentials` class (either directly or by inheritance), this constructor will clone
        it and create a new `UncCredentials` object with the same properties.
        """
        if password is None and isinstance(username, self.__class__):
            new_username = username._username
            new_password = username._password
        else:
            new_username = username
            new_password = password

        cleaned_username = clean_username(new_username) if new_username is not None else None

        if cleaned_username is None or is_valid_username(cleaned_username):
            self._username = cleaned_username
            self._password = new_password
        else:
            raise InvalidUsernameError(new_username)

    def get_username(self):
        """
        Returns the username of this `UncCredentials` object or `None` if no username was provided.
        """
        return self._username

    def get_password(self):
        """
        Returns the password of this `UncCredentials` object or `None` if no password was provided.
        """
        return self._password

    def is_empty(self):
        """
        Returns `True` if this `UncCredentials` object does not contain any meaningful credentials.
        """
        return self._username is None and self._password is None

    def get_auth_string(self):
        """
        Returns a standard representation of these credentials as a string. The string mimics
        the HTTP Basic Authentication scheme.
        """
        if self._password is not None:
            return '{0}:{1}'.format(self._username or '', self._password)
        elif self._username:
            return self._username
        else:
            return ''

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (self._username == other._username and self._password == other._password)
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(str(self))

    def __repr__(self):
        return '<{cls}: "{str}">'.format(cls=self.__class__.__name__, str=self.get_auth_string())


def get_creds_from_string(string):
    """
    Parses a standardized string from `UncCredentials`'s `get_auth_string` method into a new
    `UncCredentials` object and returns it. Whatever errors can be raised by `UncCredentials`'s
    constructor can also be raised by this function.
    """
    username, password = None, None

    if ':' in string:
        username, password = string.split(':', 1)  # Always split on the first `:` in case the
                                                   # password contains it.
    else:
        username = string

    return UncCredentials(username or None, password)  # Usernames cannot be `''`, but password can be.
