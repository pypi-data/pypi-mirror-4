# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

class ViewDocumentFromDatabase(Peer):
    from embeddedViewer import EmbeddedViewer
    from documentChanger import DocumentChanger
    from database import Database
    from viewer import Viewer

    Load = Pillow.In 

    Routings = [
        (Database.Out.RequestedDocument, Viewer.In.Document),
        (EmbeddedViewer.Out.SelectionChanged, Viewer.In.Refresh),
        (DocumentChanger.Out.SelectionChanged, Viewer.In.Refresh)
    ]

    def __init__(self, room):
        Peer.__init__(self, room)
        self._addRouting(ViewDocumentFromDatabase.In.Load, Database.In.RequestDocument)

    def initialize(self):
        pass 



