# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

class EditDocumentDialog(Peer):
    def __init__(self, room, database, id, dialog, dbClass=None, *args):
        from directEditDocument import DirectEditDocument
        from documentDatabase import DocumentDatabase
        from debugger import Debugger
        from dialog import Dialog

        Peer.__init__(self, room)
       
        self.add(DirectEditDocument(room, id))
        self.add(DocumentDatabase(room))

        self.add(Debugger(room, "*"))
        self.add(DocumentCache(room))
        self.add(Dialog(room, dialog))

        if dbClass is None:
            from couchDB import CouchDB
            self.add(CouchDB(room, queryPeer=False, databaseName=database))
        else:
            self.add(dbClass(room, queryPeer=False, databaseName=database))
