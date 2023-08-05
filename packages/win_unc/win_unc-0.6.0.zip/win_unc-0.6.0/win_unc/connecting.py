"""
Contains classes for dealing with UNC paths on Windows.
"""

from win_unc import sanitizors as S
from win_unc.disk_drive import get_available_disk_drive
from win_unc.internal.loggers import no_logging
from win_unc.internal.net_use_table import parse_net_use_table
from win_unc.internal.shell import run, ShellCommandError
from win_unc.internal.current_state import get_current_net_use_table


class UncDirectoryConnection(object):
    """
    Represents a UNC path as it relates to the current Windows session.
    """

    def __init__(self, unc, disk_drive=None, persistent=False, logger=no_logging):
        """
        Returns a new `UncDirectoryConnection` object.
        `unc` is a `UncDirectory` that describes the UNC path and necessary credentials (if
              needed).
        `disk_drive` is either `None` or a `DiskDrive`. If it is `None` then connecting this
                     `UncDirectoryConnection` will not set up to a local mount point. Otherwise,
                     this `UncDirectoryConnection` will be mounted to `disk_drive` as its local
                     mount point when connected.
        `persistent` must be `True` if the UNC directory's connection should persist for all future
                     sessions of the current Windows user.
        `logger` is a function that takes exactly one string parameter. It will be called for
                 logging purposes. By default, this is a no-op.
        """
        self.unc = unc
        self.disk_drive = disk_drive
        self.persistent = persistent
        self.logger = logger
        self._was_connected_before_enter = None  # Flag to handle context manager

    def get_path(self):
        """
        Returns the UNC path for this `UncDirectoryConnection`.
        """
        return self.unc.get_path()

    def get_username(self):
        """
        Returns the username associated with the credentials of this `UncDirectoryConnection` or
        `None` if no username was provided.
        """
        return self.unc.get_username()

    def get_password(self):
        """
        Returns the password associated with the credentials of this `UncDirectoryConnection` or
        `None` if no password was provided.
        """
        return self.unc.get_password()

    def connect(self):
        """
        Connects the UNC directory. If the comand fails, this will raise a `ShellCommandError`.
        """
        self.logger('Connecting the network UNC path "{path}".'.format(path=self.get_path()))
        self._connect_with_creds(self.get_username(), self.get_password())

    def disconnect(self):
        """
        Disconnects the UNC path. If the command fails, this will raise a `ShellCommandError`.
        """
        identifier = (self.disk_drive.get_drive() if self.disk_drive
                      else S.sanitize_path(self.unc.get_normalized_path()))
        self.logger('Disconnecting the network UNC path "{path}".'.format(path=self.get_path()))
        run('NET USE "{id}" /DELETE /YES'.format(id=identifier), self.logger)

    def is_connected(self):
        """
        Returns `True` if the system registers this `UncDirectoryConnection` as connected.
        """
        return self.get_connection_status() in ['ok', 'disconnected']

    def get_connection_status(self):
        """
        Returns one of the following based on this `UncDirectoryConnection`'s status according to
        the system:
            `'ok'`           - connected
            `'disconnected'` - recognized but inactive
            `'unavailable'`  - a previous connection attempt failed
            `None`           - not connected
        """
        net_use = get_current_net_use_table()
        matching = net_use.get_matching_rows(local=self.disk_drive, remote=self.unc)
        return matching[0]['status'] if matching else None

    def _get_connection_command(self, username=None, password=None):
        """
        Returns the Windows command to be used to connect this UNC directory.
        `username` and/or `password` are used as credentials if they are supplied.
        """
        device_str = ' "{0}"'.format(self.disk_drive) if self.disk_drive else ''
        password_str = ' "{0}"'.format(S.sanitize_for_shell(password)) if password else ''
        user_str = ' /USER:"{0}"'.format(S.sanitize_username(username)) if username else ''

        return 'NET USE{device} "{path}"{password}{user} /PERSISTENT:{persistent}'.format(
            device=device_str,
            path=S.sanitize_unc_path(self.get_path()),
            password=password_str,
            user=user_str,
            persistent='YES' if self.disk_drive and self.persistent else 'NO')

    def _connect_with_creds(self, username=None, password=None):
        """
        Constructs and executes the Windows connecting command to connect this
        `UncDirectoryConnection`.
        `username` and/or `password` are used as credentials if they are supplied. If there is an
        error a `ShellCommandError` is raised.
        """
        command = self._get_connection_command(username, password)
        self.logger(self._get_connection_command(username, '-----') if password else command)
        run(command)

    def __enter__(self):
        self._was_connected_before_enter = self.is_connected()
        if not self._was_connected_before_enter:
            self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if not self._was_connected_before_enter and self.is_connected():
            self.disconnect()
        self._was_connected_before_enter = None

    def __str__(self):
        return str(self.unc)

    def __repr__(self):
        return '<{cls}: {str}>'.format(cls=self.__class__.__name__, str=str(self))


class UncDirectoryMount(UncDirectoryConnection):
    """
    A `UncDirectoryConnection` specifically for mounting UNC paths to a local drive letter.
    """

    def __init__(self, unc, disk_drive=None, persistent=False, logger=no_logging):
        """
        Creates a `UncDirectoryConnection` with a target mount point (drive letter).
        `unc` is a `UncDirectory` that describes the UNC path and necessary credentials (if
              needed).
        `disk_drive` is either `None` or a `DiskDrive`. If it is `None`, then an available disk
                     drive on the system will be automatically selected as a local mount point or a
                     `NoDrivesAvailableError` will be raised. Otherwise, the local mount point will
                     be `disk_drive. The local mount point will be set up when this
                     `UncDirectoryMount` is mounted (i.e. connected).
        `persistent` must be `True` if the UNC directory's connection should persist for all future
                     sessions of the current Windows user.
        """
        disk_drive = disk_drive if disk_drive else get_available_disk_drive()
        super(UncDirectoryMount, self).__init__(unc, disk_drive, persistent, logger)

    def mount(self):
        """
        An alias for `UncDirectoryConnection`'s `connect` method.
        """
        self.connect()

    def unmount(self):
        """
        An alias for `UncDirectoryConnection`'s `disconnect` method.
        """
        self.disconnect()

    def is_mounted(self):
        """
        An alias for `UncDirectoryConnection`'s `is_connected` method.
        """
        return self.is_connected()
