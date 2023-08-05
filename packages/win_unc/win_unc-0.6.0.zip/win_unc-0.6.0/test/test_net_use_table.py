from unittest import TestCase

from win_unc.disk_drive import DiskDrive
from win_unc.internal.net_use_table import NetUseTable, parse_net_use_table
from win_unc.unc_directory import UncDirectory


EMPTY_TABLE = '''
New connections will be remembered.

There are no entries in the list.
'''

VALID_TABLE = r'''
New connections will be remembered.


Status       Local     Remote                    Network

-------------------------------------------------------------------------------
OK           A:        \\some.remote.path\with-a-long-path
                                                 Microsoft Windows Network
Disconnected B:        \\localhost               Microsoft Windows Network
OK           C:        \\localhost\has    spaces Microsoft Windows Network
Unavailable  D:        \\a
            Microsoft Windows Network
OK                     \\localhost\IPC$          Microsoft Windows Network
OK           LPT1:     \\some\remote\printer     Printer
The command completed successfully.

'''


class TestParsingNetUseTable(TestCase):
    """
    Tests correct parsing of the output from `NET USE`.
    """

    def assertEqualAsSets(self, a, b):
        """
        Asserts that containers `a` and `b` are equal disregarding ordering.
        """
        self.assertSetEqual(set(a), set(b))

    def test_empty_table(self):
        table = parse_net_use_table(EMPTY_TABLE)
        self.assertEqual(table.get_connected_paths(), [])
        self.assertEqual(table.get_connected_devices(), [])

    def test_valid_table(self):
        table = parse_net_use_table(VALID_TABLE)

        mounted_paths = [UncDirectory(r'\\a'),
                         UncDirectory(r'\\localhost'),
                         UncDirectory(r'\\localhost\IPC$'),
                         UncDirectory(r'\\localhost\has    spaces'),
                         UncDirectory(r'\\some.remote.path\with-a-long-path')]
        self.assertEqualAsSets(table.get_connected_paths(), mounted_paths)

        mounted_drives = [DiskDrive('A:'),
                          DiskDrive('B:'),
                          DiskDrive('C:'),
                          DiskDrive('D:')]
        self.assertEqualAsSets(table.get_connected_devices(), mounted_drives)


class TestNetUseTable(TestCase):
    """
    Tests methods of the `NetUseTable` class.
    """

    def test_get_mounted_paths(self):
        table = NetUseTable()
        self.assertEqual(table.get_connected_paths(), [])

        table.add_row({'local': 'A', 'remote': r'\\remote1', 'status': 'status'})
        self.assertEqual(table.get_connected_paths(), [UncDirectory(r'\\remote1')])

        table.add_row({'local': 'A', 'remote': r'\\remote2', 'status': 'status'})
        self.assertEqual(table.get_connected_paths(), [UncDirectory(r'\\remote1'),
                                                       UncDirectory(r'\\remote2')])

    def test_get_connected_devices(self):
        table = NetUseTable()
        self.assertEqual(table.get_connected_devices(), [])

        table.add_row({'local': 'A', 'remote': r'\\remote', 'status': 'status'})
        self.assertEqual(table.get_connected_devices(), [DiskDrive('A:')])

        table.add_row({'local': 'B', 'remote': r'\\remote', 'status': 'status'})
        self.assertEqual(table.get_connected_devices(), [DiskDrive('A:'), DiskDrive('B:')])

    def test_get_matching_rows_selecting(self):
        table = NetUseTable()

        self.assertEqual(table.get_matching_rows(), [])
        self.assertEqual(table.get_matching_rows(local=r'A'), [])

        row1 = table.add_row({'local': 'A', 'remote': r'\\remote2', 'status': 'status1'})
        row2 = table.add_row({'local': 'A', 'remote': r'\\remote1', 'status': 'status2'})
        row3 = table.add_row({'local': 'B', 'remote': r'\\remote1', 'status': 'status1'})

        self.assertEqual(table.get_matching_rows(), [row1, row2, row3])
        self.assertEqual(table.get_matching_rows(local='Z'), [])
        self.assertEqual(table.get_matching_rows(remote=r'\\remote0'), [])
        self.assertEqual(table.get_matching_rows(status='status0'), [])
        self.assertEqual(table.get_matching_rows(local='A'), [row1, row2])
        self.assertEqual(table.get_matching_rows(remote=r'\\remote1'), [row2, row3])
        self.assertEqual(table.get_matching_rows(status='status1'), [row1, row3])
        self.assertEqual(table.get_matching_rows(local='B', remote=r'\\remote2'), [])
        self.assertEqual(table.get_matching_rows(local='A', remote=r'\\remote1'), [row2])
        self.assertEqual(table.get_matching_rows(local='A', status='status1'), [row1])
        self.assertEqual(table.get_matching_rows(remote=r'\\remote1', status='status1'), [row3])

        self.assertEqual(table.get_matching_rows(local='A',
                                                 remote=r'\\remote2',
                                                 status='status1'),
                         [row1])

    def test_get_matching_rows_local_comparisons(self):
        table = NetUseTable()
        row = table.add_row({'local': 'A:', 'remote': '', 'status': ''})

        self.assertEqual(table.get_matching_rows(local='a'), [row])
        self.assertEqual(table.get_matching_rows(local='A'), [row])
        self.assertEqual(table.get_matching_rows(local='a:'), [row])
        self.assertEqual(table.get_matching_rows(local='A:'), [row])
        self.assertEqual(table.get_matching_rows(local='b:'), [])

    def test_get_matching_rows_remote_comparisons(self):
        table = NetUseTable()
        row = table.add_row({'local': '', 'remote': r'\\remote\a\IPC$', 'status': ''})

        self.assertEqual(table.get_matching_rows(remote=r'\\remote\a'), [row])
        self.assertEqual(table.get_matching_rows(remote=r'\\remote\a\\'), [row])
        self.assertEqual(table.get_matching_rows(remote=r'\\Remote\A'), [row])
        self.assertEqual(table.get_matching_rows(remote=r'\\remote\a\IPC$'), [row])
        self.assertEqual(table.get_matching_rows(remote=r'\\remote\a\ipc$'), [row])
        self.assertEqual(table.get_matching_rows(remote=r'\\remote\b'), [])

    def test_get_matching_rows_status_comparisons(self):
        table = NetUseTable()
        row = table.add_row({'local': '', 'remote': '', 'status': 'ABC'})

        self.assertEqual(table.get_matching_rows(status='ABC'), [row])
        self.assertEqual(table.get_matching_rows(status='abc'), [row])
        self.assertEqual(table.get_matching_rows(status='cba'), [])
