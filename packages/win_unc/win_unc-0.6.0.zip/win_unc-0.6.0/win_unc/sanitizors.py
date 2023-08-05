def sanitize_for_shell(string):
    """
    Return `string` with double quotes escaped for use in a Windows shell command.
    """
    return string.replace('"', r'\"')


def sanitize_username(name):
    """
    This applies only to Windows usernames (logons).
    """
    return name.translate(None, r'"/[]:;|=,+*?<>' + '\0')


def sanitize_path(path):
    """
    This applies only to Windows paths.
    """
    return path.translate(None, r'<>"/|?*' + ''.join(map(chr, range(0, 31))))


def sanitize_unc_path(path):
    return sanitize_path(path).translate(None, ':')


def sanitize_file_name(file_name):
    """
    This applies only to Windows file names.
    """
    return sanitize_path(file_name).translate(None, ':\\')
