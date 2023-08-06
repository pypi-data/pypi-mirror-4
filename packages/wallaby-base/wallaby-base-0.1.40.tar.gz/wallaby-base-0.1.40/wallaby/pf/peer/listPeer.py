# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from uiPeer import *

class ListPeer(UIPeer):
    RequestedDocument = Pillow.In
    RequestDocument = Pillow.Out

    def __init__(self, room, cb, path, source):
        UIPeer.__init__(self, room, path)
        self._cb = cb
        self._source = source
        self._catch(ListPeer.In.RequestedDocument, self._requestedDocument)
        self._initialized = False

    def initialize(self):
        if self._initialized: return
        self._initialized = True

        self._throw(ListPeer.Out.RequestDocument, self._source)

    def _requestedDocument(self, pillow, document):
        if document.documentID == self._source:
            self._cb(document)
