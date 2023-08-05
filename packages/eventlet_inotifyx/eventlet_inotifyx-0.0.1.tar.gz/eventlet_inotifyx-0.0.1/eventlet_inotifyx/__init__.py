
import os
import struct

import eventlet
from eventlet.green import select

from inotifyx import *


_EVENT_FMT = 'iIII'
_EVENT_SIZE = struct.calcsize(_EVENT_FMT)
_BUF_LEN = 1024 * (_EVENT_SIZE + 16)


def get_events(fd, timeout=None):
    (rlist, _, _) = select.select([fd], [], [], timeout)
    if not rlist:
        return []
    events = []

    while True:
        buf = os.read(fd, _BUF_LEN)
        i = 0
        while i < len(buf):
            (wd, mask, cookie, len_) = struct.unpack_from(_EVENT_FMT, buf, i)
            name = None
            if len_ > 0:
                start = i + _EVENT_SIZE
                end = start + len_
                # remove \0 terminator and padding
                name = buf[start:end].rstrip('\0')

            events.append(InotifyEvent(wd, mask, cookie, name))
            i += _EVENT_SIZE + len_

        (rlist, _, _) = select.select([fd], [], [], 0)
        if not rlist:
            break

    return events
