"""This is an automatically generated file created by stsci.distutils.hooks.version_setup_hook.
Do not modify this file by hand.
"""


import datetime


__version__ = '3.1.1'
__svn_revision__ = '2064'
__svn_full_info__ = 'Path: 3.1.1\nWorking Copy Root Path: /internal/1/root/src/PyFITS/3.1.1\nURL: https://svn6.assembla.com/svn/pyfits/tags/3.1.1\nRepository Root: https://svn6.assembla.com/svn/pyfits\nRepository UUID: ed100bfc-0583-0410-97f2-c26b58777a21\nRevision: 2064\nNode Kind: directory\nSchedule: normal\nLast Changed Author: stsci_embray\nLast Changed Rev: 1973\nLast Changed Date: 2013-01-02 15:02:12 -0500 (Wed, 02 Jan 2013)'
__setup_datetime__ = datetime.datetime(2013, 2, 28, 11, 11, 5, 723997)


def update_svn_info():
    """Update the SVN info if running out of an SVN working copy."""

    import os
    import string
    import subprocess

    global __svn_revision__
    global __svn_full_info__

    # Wind up the module path until we find the root of the project
    # containing setup.py
    path = os.path.abspath(os.path.dirname(__file__))
    dirname = os.path.dirname(path)
    setup_py = os.path.join(path, 'setup.py')
    while path != dirname and not os.path.exists(setup_py):
        path = os.path.dirname(path)
        dirname = os.path.dirname(path)
        setup_py = os.path.join(path, 'setup.py')

    try:
        pipe = subprocess.Popen(['svnversion', path],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        if pipe.wait() == 0:
            stdout = pipe.stdout.read().decode('latin1').strip()
            if stdout and stdout[0] in string.digits:
                __svn_revision__ = stdout
    except OSError:
        pass

    try:
        pipe = subprocess.Popen(['svn', 'info', path],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        if pipe.wait() == 0:
            lines = []
            for line in pipe.stdout.readlines():
                line = line.decode('latin1').strip()
                if not line:
                    continue
                lines.append(line)

            if not lines:
                __svn_full_info__ = 'unknown'
            else:
                __svn_full_info__ = '\n'.join(lines)
    except OSError:
        pass


update_svn_info()
del update_svn_info
