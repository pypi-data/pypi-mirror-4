# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

class PayloadCallback(Peer):
    def __init__(self, room, pillow, cb, raw=False):
        Peer.__init__(self, room)
        self._cb = cb
        self._raw = raw
        self._catch(pillow, self._message)

    def _message(self, pillow, feather):
        if self._raw:
            self._cb(feather)
        else:
            self._cb(unicode(feather))
