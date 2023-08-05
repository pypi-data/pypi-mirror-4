class WinUncError(Exception):
    """
    Generic error class for all errors raised by the win_unc library.
    """
    pass


class UncDirectoryError(WinUncError):
    """
    Generic error class for all errors raised by `UncDirectory`.
    """
    pass


class InvalidUncPathError(UncDirectoryError):
    """
    Error for the case when the library user supplies an invalid UNC path.
    """

    def __init__(self, path):
        self.path = path

    def __str__(self):
        return 'The UNC path "{0}" is invalid.'.format(self.path)


class InvalidUsernameError(UncDirectoryError):
    """
    Error for the case when the library user supplies an invalid username for UNC credentials.
    """

    def __init__(self, username):
        self.username = username

    def __str__(self):
        return 'The username "{0}" is invalid.'.format(self.username)


class InvalidDiskDriveError(WinUncError):
    """
    Error for the case when the library user supplies and invalid drive letter when creating a
    `DiskDrive`.
    """

    def __init__(self, drive):
        self.drive = drive

    def __str__(self):
        return 'The disk drive "{0}" is invalid. Valid drives are A through Z (e.g. "C:").'.format(
            self.drive)


class NoDrivesAvailableError(WinUncError):
    """
    Error for the case when Windows has no drive letters available to be mapped.
    """

    def __str__(self):
        return 'The system has no drive letters available.'


class ShellCommandError(WinUncError):
    """
    Error for the case when a Windows shell command returns an error code.
    """

    def __init__(self, command=None, error_code=None):
        """
        Both `command` and `error_code` are optional. The more information that is provided here,
        the more descriptive the error message will be.
        `command` is a string representing the command that was executed in the shell.
        `error_code` is the numeric error code returned by executing `command`.
        """
        self.command = command
        self.error_code = error_code

    def __str__(self):
        if self.command and self.error_code:
            return 'The command `{command}` exited with error code {code}.'.format(
                command=self.command, code=self.error_code)
        elif self.command:
            return 'The command `{command}` exited with an error.'.format(command=self.command)
        elif self.error_code:
            return 'Command exited with error code {code}.'.format(code=self.error_code)
        else:
            return 'Command exited with an error.'
