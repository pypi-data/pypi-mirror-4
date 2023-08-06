# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

from roomDebugger import RoomDebugger
from documentChanger import DocumentChanger
# from credentials import Credentials
from listPeer import ListPeer
from viewer import Viewer
from editor import Editor

class RoomDebuggerRouting(Peer):
   
    Sending = [
        Viewer.In.Document,
        Editor.In.Enable,
        RoomDebugger.In.RequestDebugInfo,
        ListPeer.In.RequestedDocument
    ]

    Receiving = [
        RoomDebugger.Out.RequestedRooms,
        Editor.Out.FieldChanged
    ]

    Routings = [
        (RoomDebugger.Out.RequestedRooms, ListPeer.In.RequestedDocument),
        (RoomDebugger.Out.RequestedRooms, Viewer.In.Document),
        (ListPeer.Out.RequestDocument, RoomDebugger.In.RequestRooms),
        (RoomDebugger.Out.RequestedDebugInfo, Viewer.In.Document),
        (DocumentChanger.Out.SelectionChanged, Viewer.In.Refresh)
    ]

    # FIXME: (RoomDebugger.Out.RequestedActions, Viewer.In.Document),

    def __init__(self, room):
        Peer.__init__(self, room)

        self._roomDocument = None

        self._catch(Editor.Out.FieldChanged, self._fieldChanged)
        self._catch(RoomDebugger.Out.RequestedRooms, self._rooms)

    def initialize(self):
        # FIXME: self._throw(Credentials.Out.Credential, Document())
        self._throw(Editor.In.Enable, True)

    def _fieldChanged(self, pillow, path):
        if path == 'room':
            if self._roomDocument != None:
                room = self._roomDocument.get(path)

            self._throw(RoomDebugger.In.RequestDebugInfo, room)

    def _rooms(self, pillow, document):
        self._roomDocument = document 
        self._throw(ListPeer.In.RequestedDocument, document)
        self._throw(Viewer.In.Document, document)
