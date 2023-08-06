# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

class DocumentViewer(Peer):
    from documentCache import DocumentCache
    from viewer import Viewer

    Routings = [
        (DocumentCache.Out.RequestedDocument, Viewer.In.Document)
    ]

    def __init__(self, room):
        Peer.__init__(self, room)
