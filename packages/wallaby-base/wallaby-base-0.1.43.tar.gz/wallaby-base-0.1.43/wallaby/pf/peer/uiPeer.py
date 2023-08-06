# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

class UIPeer(Peer):
    def __init__(self, room, path=None):
        Peer.__init__(self, room)
        self._roomName = room
        self._path = path

        from credentialsConsumer import CredentialsConsumer
        self._cc = CredentialsConsumer(self._newCredentials)
        self._credentials = None

    def destroy(self, remove=False):
        Peer.destroy(self, remove)
    
        if self._cc: self._cc.destroy(remove)
        self._cc = None

    def _newCredentials(self, pillow, feathers):
        self._credentials = feathers
        self._refresh(None, self._path)

    def _refresh(self, pillow, path):
        pass
