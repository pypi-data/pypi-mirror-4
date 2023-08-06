import time

import win32api
import win32con
import win32file


def setctime(path, ctime=None):
    """ Set the creation time of the file specified by path.
    If ctime is None, then the file's creation time is set to the current time.
    The argument ctime is a number giving the number of seconds since the epoch (see the time module).
    """
    if ctime is None:
        ctime = time.time()
    hFile = win32file.CreateFile(
        path,
        win32con.GENERIC_WRITE,
        win32con.FILE_SHARE_READ,
        None,
        win32con.OPEN_EXISTING,
        win32con.FILE_ATTRIBUTE_NORMAL | win32con.FILE_FLAG_BACKUP_SEMANTICS,
        None)
    try:
        win32file.SetFileTime(hFile, ctime, None, None)
    finally:
        win32api.CloseHandle(hFile)
