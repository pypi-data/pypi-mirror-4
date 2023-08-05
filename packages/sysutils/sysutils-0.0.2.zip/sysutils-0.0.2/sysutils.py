import os
import datetime
import string
from ctypes import windll
import subprocess
from contextlib import contextmanager
import win32wnet
from win32netcon import RESOURCETYPE_DISK as DISK


def purge_directory(path, days):
    """Delete files in the given path that are older than
    the supplied number of days"""
    for f in os.listdir(path):
        fullpath = os.path.join(path, f)
        timestamp = os.stat(fullpath).st_ctime
        createtime = datetime.datetime.fromtimestamp(timestamp)
        now = datetime.datetime.now()
        delta = now - createtime
        if os.path.isfile(fullpath) and delta.days > days:
            os.remove(fullpath)


def get_drives():
    """Get a list of 'in-use' drive letters"""
    drives = []
    bitmask = windll.kernel32.GetLogicalDrives()
    for letter in string.uppercase:
        if bitmask & 1:
            drives.append(letter)
        bitmask >>= 1
    return drives


def get_free_drive_letter():
    """Get a drive letter that is free for use"""
    letters = set(string.uppercase)
    used = set(get_drives())
    return list(letters - used)[-1]


def disconnect_drive(letter):
    """Disconnects a mapped drive"""
    win32wnet.WNetCancelConnection2(letter, 1, 1)


def connect_drive(sharename, user=None, password=None, letter=None):
    """Map a drive to the given windows share, optionally using username
    and password"""
    letter = letter or get_free_drive_letter() + ':'
    win32wnet.WNetAddConnection2(DISK, letter, sharename, None, user,
                                 password, 0)
    return letter


@contextmanager
def map_drive(sharename, user=None, password=None, letter=None):
    """Maps a drive in a with-block, closing it at block completion"""
    try:
        letter = connect_drive(sharename, user, password, letter)
        yield letter
    finally:
        disconnect_drive(letter)
