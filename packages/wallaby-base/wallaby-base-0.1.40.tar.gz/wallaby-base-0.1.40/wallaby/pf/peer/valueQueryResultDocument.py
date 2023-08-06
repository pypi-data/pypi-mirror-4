# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

class ValueQueryResultDocument(Peer):
    from valueQueryResult import ValueQueryResult
    from documentCache import DocumentCache
    from database import Database

    Routings = [
        (DocumentCache.Out.RequestedDocument, ValueQueryResult.In.RequestedDocument),
        (ValueQueryResult.Out.RequestDocument, DocumentCache.In.RequestDocument),
        (ValueQueryResult.Out.SaveDocument, Database.In.SaveDocument),
    ]

    def __init__(self, room):
        Peer.__init__(self, room)
