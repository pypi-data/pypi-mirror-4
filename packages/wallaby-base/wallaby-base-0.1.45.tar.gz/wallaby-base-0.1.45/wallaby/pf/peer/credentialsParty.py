#!/usr/bin/env python
# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.


from peer import *

class CredentialsParty(Peer):
    def __init__(self, database=None, dbClass=None, *args, **ka):
        room = "__CREDENTIALS__"
        Peer.__init__(self, room)

        from documentDatabase import DocumentDatabase
        from documentCache import DocumentCache
        from documentCredentialsDocument import DocumentCredentialsDocument
        from documentCredentials import DocumentCredentials
        from credentialsRouting import CredentialsRouting
        from debugger import Debugger

        # Routings...
        self.add(DocumentDatabase(room))
        self.add(DocumentCredentialsDocument(room))
        self.add(CredentialsRouting(room))

        # Peers...
        self.add(Debugger(room))
        self.add(DocumentCache(room))
        self.add(DocumentCredentials(room))

        if dbClass is None:
            from couchDB import CouchDB
            self.add(CouchDB(room, query=False, databaseName=database, **ka))
        else:
            self.add(dbClass(room, query=False, databaseName=database, **ka))


