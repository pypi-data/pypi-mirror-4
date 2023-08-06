# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

from database import Database

class ReplicateDatabase(Peer):

    Sending = [
        Database.In.SaveDocument
    ]

    Receiving = [
        Database.In.SaveDocument,
        Database.Out.RequestedDocument
    ]

    def __init__(self, srcRoom, dstRoom):
        Peer.__init__(self, srcRoom)

        self._dstRoom = House.get(dstRoom)

        self._catch(Database.In.SaveDocument, self._saveInDst)
        self._catch(Database.Out.Document, self._replicate)

    def _saveInDst(self, pillow, feathers):
        self._dstRoom.throw(pillow, feathers, me=self)

    def _replicate(self, pillow, feathers):
        self._dstRoom.throw(Database.In.SaveDocument, (feathers, None), me=self)
