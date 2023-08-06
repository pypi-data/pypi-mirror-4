# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

from multiViewer import MultiViewer
from viewer import Viewer
from editor import Editor

class MultiViewEditor(Peer):
    Description = ("Routing between editor elements and the query document of a multi-view element (like a table)",
                    '{ "dstRoom": null, "pillow": "MultiViewer.In.Refresh" }')

    Receiving = [
        MultiViewer.Out.QueryDocument,
        Editor.Out.FieldChanged
    ] 

    Sending = [
        Editor.In.Enable
    ]

    Routings = [
        (MultiViewer.Out.QueryDocument, Viewer.In.Document),
        (Editor.Out.FieldChanged, Viewer.In.Refresh)
    ]

    def __init__(self, room, dstRoom=None, pillow="MultiViewer.In.Refresh"):
        Peer.__init__(self, room)
       
        self._dstRoom = dstRoom
        self._pillow = pillow

        self._catch(MultiViewer.Out.QueryDocument, self._enable)

        if dstRoom is not None:
            self._catch(Editor.Out.FieldChanged, self._fieldChanged)

    def _fieldChanged(self, pillow, feathers):
        if self._dstRoom:
            self._throw(self._dstRoom + ":" + self._pillow, None)

    def _enable(self, pillow, feathers):
        self._throw(Editor.In.Enable, True)

    def initialize(self):
        pass 



