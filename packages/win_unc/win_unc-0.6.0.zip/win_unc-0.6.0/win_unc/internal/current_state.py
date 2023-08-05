from win_unc.internal.net_use_table import parse_net_use_table
from win_unc.internal.shell import run


def get_current_net_use_table():
    """
    Returns a `NetUseTable` that describes the current Windows session's status regarding
    all UNC paths.
    """
    stdout, _ = run('NET USE')
    return parse_net_use_table(stdout)
