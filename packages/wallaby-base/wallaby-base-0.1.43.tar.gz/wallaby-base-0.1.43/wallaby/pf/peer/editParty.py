# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *
from editDocument import EditDocument

class EditParty(Peer):

    def __init__(self, room, database=None, docId=None, dbClass=None, *args, **ka):
        Peer.__init__(self, room)

        from documentDatabase import DocumentDatabase
        from documentCache import DocumentCache
        from enableDocument import EnableDocument
        from debugger import Debugger
        from dialog import Dialog

        self._docId = docId

        self.add(DocumentDatabase(room))

        # Peers...
        self.add(Debugger(room))
        self.add(DocumentCache(room))
        self.add(EditDocument(room))
        self.add(EnableDocument(room))

        if dbClass is None:
            # try CouchDB as default
            from couchDB import CouchDB
            self.add(CouchDB(room, query=False, databaseName=database, **ka))
        else:
            self.add(dbClass(room, query=False, databaseName=database, **ka))

    def initialize(self):
        if self._docId != None:
            self._throw(EditDocument.In.Load, self._docId)
