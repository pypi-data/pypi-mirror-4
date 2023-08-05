from distutils.core import setup

from win_unc import __version__


setup(
    name='win_unc',
    packages=['win_unc', 'win_unc.internal'],
    version=__version__,
    description='UNC network drive handling and mounting for Windows',
    author='Elliot Cameron',
    author_email='elliot.cameron@covenanteyes.com',
    url='https://github.com/CovenantEyes/py_win_unc',
    download_url='https://github.com/CovenantEyes/py_win_unc/zipball/v' + __version__,
    keywords=['directory', 'folder', 'unc', 'local', 'remote', 'path'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    long_description="""
win_unc
=======

A Python library for handling UNC paths on Windows.

With this library you can

  * Connect UNC directories to your Windows session
  * Connect UNC directories requiring authorization
    by providing credentials
  * Mount UNC directories (with or without credentials)
    to a local mount point
  * Disconnect/unmount UNC connections
  * Query existing UNC connections known by the
    Windows session

Full documentation is at http://covenanteyes.github.com/py_win_unc

Report any issues on the package's GitHub page: http://github.com/CovenantEyes/py_win_unc

Installation
============

To install::

    $ pip install win_unc


Sneak Preview
=============

Below is a simple example::

    from win_unc import UncDirectoryMount, UncDirectory, DiskDrive

    conn = UncDirectoryMount(UncDirectory(r'\\home\shared'), DiskDrive('Z:'))
    conn.mount()
    print 'Drive connected:', conn.is_mounted()
    conn.unmount()

You can also provide credentials like this::

    from win_unc import UncCredentials

    unc = UncDirectory(r'\\home\shared', UncCredentials('user', 'pwd'))
    conn = UncDirectoryMount(unc, DiskDrive('Z:'))

Or just connect the path without mounting it::

    from win_unc import UncDirectoryConnection

    conn = UncDirectoryConnection(r'\\home\shared')
    conn.connect()

""",
)
