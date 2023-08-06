# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *
from viewer import Viewer

class DocumentPathEnabler(Peer):

    def __init__(self, room, cb, enablePath, enablePathValue):
        Peer.__init__(self, room)
        self._cb = cb
        self._viewer = Viewer(room, self._enable, enablePath, raw=True)
        self._enablePathValue = enablePathValue
        self._countValue = False
        self._count = None
        self._operator = None

        if self._enablePathValue and self._enablePathValue.startswith('#'):
            self._countValue = True
            self._operator = self._enablePathValue[1:2]
            self._count = int(self._enablePathValue[2:])

    def _enable(self, value):
        if self._countValue:
            if value != None and isinstance(value, list):
                l = len(value)
                if (self._operator == '=' and l == self._count) or \
                   (self._operator == '>' and l > self._count) or \
                   (self._operator == '<' and l < self._count):
                    self._cb(True)
                    return

            self._cb(False)
            return

        if value == self._enablePathValue or unicode(value) == unicode(self._enablePathValue):
            self._cb(True)
            return

        self._cb(False)
