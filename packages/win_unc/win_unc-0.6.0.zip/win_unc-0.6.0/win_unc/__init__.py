"""
Exports version information for this library and the most commonly used classes and functions.
"""

from win_unc.connecting import UncDirectoryConnection, UncDirectoryMount
from win_unc.disk_drive import DiskDrive
from win_unc.unc_credentials import UncCredentials
from win_unc.unc_directory import UncDirectory


__version__ = '0.6.0'
VERSION = tuple(map(int, __version__.split('.')))

__all__ = ['UncDirectoryConnection',
           'UncDirectoryMount',
           'DiskDrive',
           'UncCredentials',
           'UncDirectory']
