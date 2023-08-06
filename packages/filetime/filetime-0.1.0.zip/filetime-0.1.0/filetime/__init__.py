""" filetime - simple API for manipulating file times """

__all__ = [
    'getatime',
    'setatime',
    'getmtime',
    'setmtime',
    'getctime',
    'setctime',
]

import os
import sys
import time

getmtime = os.path.getmtime
getatime = os.path.getatime
getctime = os.path.getctime

if sys.platform == 'win32':
    import nt_setctime
    setctime = nt_setctime.setctime


def setmtime(path, mtime=None):
    """ Set the modified time of the file specified by path.
    If mtime is None, then the file's modified time is set to the current time.
    The argument mtime is a number giving the number of seconds since the epoch (see the time module).
    """
    if mtime is None:
        mtime = time.time()
    atime = getatime(path)
    os.utime(path, (atime, mtime))

def setatime(path, atime=None):
    """ Set the access time of the file specified by path.
    If atime is None, then the file's access time is set to the current time.
    The argument atime is a number giving the number of seconds since the epoch (see the time module).
    """
    if atime is None:
        atime = time.time()
    mtime = getmtime(path)
    os.utime(path, (atime, mtime))
