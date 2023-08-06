# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

class DocumentCredentialsDocument(Peer):
    from documentCache import DocumentCache
    from documentCredentials import DocumentCredentials
    from database import Database

    Routings = [
        (DocumentCache.Out.RequestedDocument, DocumentCredentials.In.RequestedDocument),
        (Database.Out.DocumentNotFound, DocumentCredentials.In.DocumentNotFound),
        (Database.Out.DocumentCreated, DocumentCredentials.In.DocumentCreated),
        (DocumentCredentials.Out.RequestDocument, DocumentCache.In.RequestDocument),
        (DocumentCredentials.Out.SaveDocument, Database.In.SaveDocument)
    ]

    def __init__(self, room):
        Peer.__init__(self, room)
