# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

class ListDocumentCache(Peer):
    from documentCache import DocumentCache
    from listPeer import ListPeer

    Routings = [
        (DocumentCache.Out.RequestedDocument, ListPeer.In.RequestedDocument),
        (DocumentCache.Out.DocumentChanged, ListPeer.In.RequestedDocument),
        (ListPeer.Out.RequestDocument, DocumentCache.In.RequestDocument)
    ]

    def __init__(self, room):
        Peer.__init__(self, room)
