from win_unc.connecting import UncDirectoryConnection, UncDirectoryMount
from win_unc.internal.current_state import get_current_net_use_table


__all__ = ['get_current_connections', 'get_connection_for_unc_directory', 'get_connection_for_disk_drive']


def get_current_connections():
    """
    Returns a list of `UncDirectoryConnection` or `UncDirectoryMount` objects. Each object
    represents a connection or mount currently recognized by the system.
    """
    net_use = get_current_net_use_table()
    return [_get_connection_or_mount(row['remote'], row['local']) for row in net_use.rows]


def get_connection_for_unc_directory(unc):
    """
    Returns a `UncDirectoryConnection` or `UncDirectoryMount` representing a connected or mounted
    UNC directory that matches a given UNC directory (`unc`) or `None` if no system connections or
    mounts match `unc`.
    `unc` is a `UncDirectory`.
    """
    net_use = get_current_net_use_table()
    matching = net_use.get_matching_rows(remote=unc)
    return _get_connection_or_mount(matching[0]['remote'], matching[0]['local']) if matching else None


def get_connection_for_disk_drive(disk_drive):
    """
    Returns a `UncDirectoryMount` representing a mounted UNC directory that matches a disk drive
    (`disk_drive`) or `None` if no system mounts match `disk_drive`.
    `disk_drive` is a `DiskDrive`.
    """
    net_use = get_current_net_use_table()
    matching = net_use.get_matching_rows(local=disk_drive)
    return UncDirectoryMount(matching[0]['remote'], matching[0]['local']) if matching else None


def _get_connection_or_mount(unc, disk_drive=None):
    return UncDirectoryMount(unc, disk_drive) if disk_drive else UncDirectoryConnection(unc)
