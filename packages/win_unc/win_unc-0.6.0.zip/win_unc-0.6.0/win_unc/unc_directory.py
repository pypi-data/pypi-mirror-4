from win_unc.errors import InvalidUncPathError
from win_unc.cleaners import clean_unc_path
from win_unc.unc_credentials import get_creds_from_string
from win_unc.validators import is_valid_unc_path


class UncDirectory(object):
    """
    Represents a UNC directory on Windows. A UNC directory is a path and optionally a set of
    credentials that are required to connect to the UNC path.
    """

    def __init__(self, path, creds=None):
        """
        Returns a new `UncDirectory` class.
        `path` must be a UNC directory path. If `path` cannot be construed as a valid UNC path,
               this will raise an `InvalidUncPathError`.
        `creds` may be `None` or a `UncCrednetials` object. If `None`, then the UNC directory
                must not require authentication to be connected. Otherwise, `creds` will be used
                for authentication.

        If only the first positional argument is provided and it is already an instance of the
        `UncDirectory` class (either directly or by inheritance), this constructor will clone
        it and create a new `UncDirectory` object with the same properties. Note that the clone
        is a "shallow" clone. Both the original `UncDirectory` object and its clone will use the
        same `UncCredentials` object if it was provided.
        """

        if creds is None and isinstance(path, UncDirectory):
            new_path = path._path
            new_creds = path._creds
        else:
            new_path = path
            new_creds = creds

        cleaned_path = clean_unc_path(new_path)
        if is_valid_unc_path(cleaned_path):
            self._path = cleaned_path
            self._creds = new_creds if new_creds and not new_creds.is_empty() else None
        else:
            raise InvalidUncPathError(new_path)

    def get_normalized_path(self):
        """
        Returns the normalized path for this `UncDirectory`. Differing UNC paths that all point to
        the same network location will have the same normalized path.
        """
        path = self._path.lower()
        return path[:-5] if path.endswith(r'\ipc$') else path.rstrip('\\')

    def get_path(self):
        """
        Returns the UNC path for this `UncDirectory`.
        """
        return self._path

    def get_username(self):
        """
        Returns the username associated with the credentials of this `UncDirectory` or `None`
        if no username was provided.
        """
        return self._creds.get_username() if self._creds else None

    def get_password(self):
        """
        Returns the password associated with the credentials of this `UncDirectory` or `None`
        if no password was provided.
        """
        return self._creds.get_password() if self._creds else None

    def get_auth_string(self):
        """
        Returns the authorization string associated with the credentials of this `UncDirectory`.
        """
        return self._creds.get_auth_string() if self._creds else ''

    def get_auth_path(self):
        """
        Returns the path of this `UncDirectory` with the authorization string prepended. If this
        `UncDirectory` has no associated credentials, the returned path will be the
        `UncDirectory`'s path unmodified. Otherwise, the returned path will resemble the HTTP
        Basic Authentication scheme in its format.
        """
        creds = self.get_auth_string()
        return '{creds}{at}{path}'.format(
            creds=creds,
            at='@' if creds else '',
            path=self._path)

    def __eq__(self, other):
        if isinstance(other, UncDirectory):
            return (self.get_normalized_path() == other.get_normalized_path()
                    and self._creds == other._creds)
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        return self.get_auth_path()

    def __repr__(self):
        return '<{cls}: "{str}">'.format(cls=self.__class__.__name__, str=self.get_auth_path())


def is_unc_directory_string(string):
    """
    Returns `True` when `string` represents a `UncDirectory` as defined by `UncDirectory`'s
    `get_auth_path` method or `False` otherwise.
    """
    cleaned_string = clean_unc_path(string)
    return (is_valid_unc_path(cleaned_string)
            or ('@\\\\' in cleaned_string
               and len(cleaned_string.partition('@\\\\')[2]) > 0))


def get_unc_directory_from_string(string):
    """
    Parses a string from `UncDirectory`'s `get_auth_path` method and returns a new `UncDirectory`
    object based on it. This may raise any errors that can be raised by `UncDirectory`'s
    constructor.
    """
    creds = None
    path = string

    if '@\\\\' in string:
        creds_part, path_part = string.rsplit(r'@\\', 1)  # Always split on the last `@\\` in case
                                                          # the password contains it.
        path = r'\\' + path_part
        creds = get_creds_from_string(creds_part)

    return UncDirectory(path, creds)
