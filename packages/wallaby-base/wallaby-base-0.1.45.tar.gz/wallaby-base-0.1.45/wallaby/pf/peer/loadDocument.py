# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

class LoadDocument(Peer):

    def __init__(self, srcRoom, dstRoom=None, path=None, pillow='EditDocument.In.Load'):
        from viewer import Viewer

        Peer.__init__(self, srcRoom)
        self._dstRoom = dstRoom
        self._pillow = pillow

        self._peer = Viewer(srcRoom, self._loadDocument, path)

    def destroy(self, remove=False):
        Peer.destroy(self, remove)
        if self._peer: self._peer.destroy(remove)

    def _loadDocument(self, value):
        self._throw(self._dstRoom + ':' + self._pillow, value)
