from __future__ import absolute_import

import errno
import os
import sys
import __builtin__

if sys.version_info[0] == 3:
    bytes = bytes
else:
    try:
        _bytes = __builtin__.bytes
    except AttributeError:
        _bytes = str

    class bytes(_bytes):  # noqa

        def __new__(cls, *args):
            if len(args) > 1:
                return _bytes(args[0]).encode(*args[1:])
            return _bytes(*args)

try:
    closerange = os.closerange
except AttributeError:

    def closerange(fd_low, fd_high):  # noqa
        for fd in reversed(xrange(fd_low, fd_high)):
            try:
                os.close(fd)
            except OSError, exc:
                if exc.errno != errno.EBADF:
                    raise
