# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

class DocumentDatabase(Peer):
    Description = "Routing between document cache and database"

    from documentCache import DocumentCache
    from database import Database

    Routings = [
        (DocumentCache.Out.RequestDocument, Database.In.RequestDocument),
        (DocumentCache.Out.SaveDocument, Database.In.SaveDocument),
        (DocumentCache.Out.CreateDocument, Database.In.CreateDocument),
        (DocumentCache.Out.CreateAndSaveDocument, Database.In.CreateAndSaveDocument),
        (DocumentCache.Out.DeleteDocument, Database.In.DeleteDocument),
        (Database.Out.RequestedDocument, DocumentCache.In.RequestedDocument),
        (Database.Out.DocumentChanged, DocumentCache.In.DocumentChanged),
        (Database.Out.NewDocument, DocumentCache.In.DocumentCreated),
        (Database.Out.DocumentSaved, DocumentCache.In.DocumentSaved),
        (Database.Out.DocumentCreated, DocumentCache.In.DocumentSaved)
    ]

    def __init__(self, room): Peer.__init__(self, room)
