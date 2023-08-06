# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *
from editDocument import EditDocument

class ConfigParty(Peer):

    def __init__(self, room, database=None, docId=None, inspectorDb=None, dbClass=None, *args, **ka):
        Peer.__init__(self, room)

        from database import Database
        from documentDatabase import DocumentDatabase
        from documentCache import DocumentCache
        from enableDocument import EnableDocument
        from documentChanger import DocumentChanger
        from debugger import Debugger
        from dialog import Dialog

        self._docId = docId
        self._inspectorDb = inspectorDb

        # Peers...
        self.add(Debugger(room))
        self.add(DocumentCache(room))
        self.add(EditDocument(room, ignoreNotFound=True))
        self.add(EnableDocument(room))
        self.add(DocumentChanger(room))

        if dbClass is None:
            # try CouchDB as default
            from couchDB import CouchDB
            self.add(CouchDB(room, query=False, databaseName=database, **ka))
        else:
            self.add(dbClass(room, query=False, databaseName=database, **ka))

        Routings = [
            (DocumentCache.Out.SaveDocument, Database.In.SaveDocument),
            (DocumentCache.Out.CreateDocument, Database.In.CreateDocument),
            (DocumentCache.Out.CreateAndSaveDocument, Database.In.CreateAndSaveDocument),
            (DocumentCache.Out.DeleteDocument, Database.In.DeleteDocument),
            (Database.Out.DocumentChanged, DocumentCache.In.DocumentChanged),
            (Database.Out.NewDocument, DocumentCache.In.DocumentCreated),
            (Database.Out.DocumentSaved, DocumentCache.In.DocumentSaved),
            (Database.Out.DocumentCreated, DocumentCache.In.DocumentSaved),
            (DocumentCache.Out.RequestDocument, Database.In.RequestDocument) 
        ]

        self._catch(Database.Out.DocumentNotFound, self._notFound)

        if inspectorDb != None:
            self._catch(Database.Out.RequestedDocument, self._requestedDocument)
        else:
            Routings.append( (Database.Out.RequestedDocument, DocumentCache.In.RequestedDocument) )

        for routing in Routings: self._addRouting(*routing) 

    def _notFound(self, pillow, docId):
        if docId == self._docId:
            from wallaby.common.document import Document
            doc = Document(self._docId)
            self._requestedDocument(pillow, doc)

    @defer.inlineCallbacks
    def _requestedDocument(self, pillow, doc):
        if doc is not None:
            if doc.documentID == self._docId: 
                if self._inspectorDb != None:
                    inspectorDoc = {}
                    try:
                        import wallaby.backends.couchdb as couch
                        defaultDB = couch.Database.getDatabase()                
                        couch.Database.setURLForDatabase(self._inspectorDb, couch.Database.getURLForDatabase(None)) # default
                
                        user, password = defaultDB.credentials()
                        if user != None and password != None:
                            couch.Database.setLoginForDatabase(self._inspectorDb, user, password)

                        db = couch.Database.getDatabase(self._inspectorDb)
                        print db._url
                        inspectorDoc = yield db.get("WallabyApp2")
                        if inspectorDoc == None: inspectorDoc = None
                    except Exception as e:
                        print "No inspector Doc found", e

                    widgets = {}
                    if inspectorDoc != None and "widgets" in inspectorDoc: widgets = inspectorDoc["widgets"]
                    for k, v in widgets.items(): doc.set("widgets." + k, v)

            from documentCache import DocumentCache
            self._throw(DocumentCache.In.RequestedDocument, doc)

    def initialize(self):
        if self._docId != None:
            self._throw(EditDocument.In.Load, self._docId)
