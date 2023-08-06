# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

class CredentialsConsumer(Peer):
    Credential = Pillow.InState

    def __init__(self, callback=None):
        room = "__CREDENTIALS__"

        Peer.__init__(self, room)
        self._roomName = room
        self._callback = callback
        self._credentials = None

        # Register for credential documents
        self._catch(CredentialsConsumer.In.Credential, self._newCredentials)

    def _newCredentials(self, pillow, feathers):
        if self._callback:
            self._callback(pillow, feathers)
