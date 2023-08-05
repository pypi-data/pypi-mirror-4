win_unc
=======

Python library for handling UNC mounting on Windows. - |TravisBadge|_

.. |TravisBadge| image:: https://secure.travis-ci.org/CovenantEyes/py_win_unc.png?branch=master
.. _TravisBadge: http://travis-ci.org/CovenantEyes/py_win_unc


Installation
------------

To install::

    $ pip install win_unc


Documentation
=============

Full documentation is available at `covenanteyes.github.com/py_win_unc`_.

.. _covenanteyes.github.com/py_win_unc: http://covenanteyes.github.com/py_win_unc/

Basic Examples
--------------

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


Unit Testing
============

To run the unit tests, do the following::

    $ python test/run_tests.py

For all the tests to run, you must perform them on a Windows machine::

    > python test\run_tests.py


License
=======

This package is released under the
`MIT License`_. (See LICENSE.txt.)

.. _MIT License: http://www.opensource.org/licenses/mit-license.php
