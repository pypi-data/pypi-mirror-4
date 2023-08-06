# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

class IdQueryResultDocument(Peer):
    from documentIDQueryResult import DocumentIDQueryResult
    from documentCache import DocumentCache
    from database import Database

    Description = "Routing between a ID-based view widget and a document provider (like a document-cache)"

    Routings = [
        (DocumentCache.Out.RequestedDocument, DocumentIDQueryResult.In.RequestedDocument),
        (DocumentIDQueryResult.Out.RequestDocument, DocumentCache.In.RequestDocument)
    ]

    def __init__(self, room):
        Peer.__init__(self, room)
