# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

from viewer import Viewer

class Observer(Peer):
    from editor import Editor
    from documentChanger import DocumentChanger

    Sending = [
        Viewer.In.Document
    ]

    Routings = [
        (Editor.Out.FieldChanged, Viewer.In.Refresh),
        (DocumentChanger.Out.SelectionChanged, Viewer.In.Refresh)
    ]

    def __init__(self, room):
        Peer.__init__(self, room)

    def initialize(self):
        from wallaby.pf.room import House
        observer = House.observer()

        from wallaby.common.document import Document
        doc = Document()

        peerNames = sorted(observer.allPeers().keys())

        peers = []

        for peer in peerNames:
            ibp = observer.inBoundPillows(peer)
            obp = observer.outBoundPillows(peer)

            peers.append({
                "name": peer,
                "inBound": ibp,
                "outBound": obp
            })

        doc.set("peers", peers)
        self._throw(Viewer.In.Document, doc)
        
        # Wildcard credentials
        from credentials import Credentials
        self._throw(Credentials.Out.Credential, Document())
