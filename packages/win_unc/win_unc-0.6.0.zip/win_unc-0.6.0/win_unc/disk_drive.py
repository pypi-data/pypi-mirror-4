"""
Class for representing a Windows disk drive.
"""

import os
import string

from win_unc.cleaners import clean_drive_letter
from win_unc.errors import NoDrivesAvailableError, InvalidDiskDriveError
from win_unc.validators import is_valid_drive_letter


class DiskDrive(object):
    """
    Represents a Windows disk drive. Disk drives are always identified by a single alphabet
    character. They may map to hardware devices, local directories, or remote directories.
    """

    def __init__(self, drive):
        """
        Creates a `DiskDrive` from a `drive`.
        `drive` must be the path to a Windows disk drive (from 'A:' to 'Z:', case-insensitive).

        If only the first positional argument is provided and it is already an instance of the
        `DiskDrive` class (either directly or by inheritance), this constructor will clone
        it and create a new `DiskDrive` object with the same properties.
        """
        new_letter = drive._drive_letter if isinstance(drive, self.__class__) else drive
        cleaned_letter = clean_drive_letter(new_letter)

        if is_valid_drive_letter(cleaned_letter):
            self._drive_letter = cleaned_letter
        else:
            raise InvalidDiskDriveError(new_letter)

    def get_drive(self):
        """
        Returns this `DiskDrive`'s path. The path will always be an upper-case letter followed by
        a colon (`:`). For example, if the drive letter is "G", then this will return "G:".
        """
        return self._drive_letter + ':'

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.get_drive() == other.get_drive()
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        return self.get_drive()

    def __repr__(self):
        return '<{cls}: {str}>'.format(cls=self.__class__.__name__, str=self.get_drive())


def get_available_disk_drive():
    """
    Returns the first available Windows disk drive. The search starts with "Z" since the later
    letters are not as commonly mapped. If the system does not have any drive letters available
    this will raise a `NoDrivesAvailableError`.
    """
    for letter in reversed(string.ascii_uppercase):
        if not os.path.isdir(letter + ':\\'):
            return DiskDrive(letter)
    else:
        raise NoDrivesAvailableError()
