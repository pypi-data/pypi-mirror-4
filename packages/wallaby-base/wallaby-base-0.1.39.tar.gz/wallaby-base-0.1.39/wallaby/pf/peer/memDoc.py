# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

from multiViewer import MultiViewer
from viewer import Viewer
from editor import Editor

class MemDoc(Peer):

    Routings = [
        (Editor.Out.FieldChanged, Viewer.In.Refresh)
    ]

    def __init__(self, room):
        Peer.__init__(self, room)
       
    def initialize(self):
        from wallaby.common.document import Document
        self._throw(Viewer.In.Document, Document())
        self._throw(Editor.In.Enable, True)



