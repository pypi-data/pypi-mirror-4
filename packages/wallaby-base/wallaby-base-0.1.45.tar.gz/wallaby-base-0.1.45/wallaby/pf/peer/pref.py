# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

from documentCache import DocumentCache
from viewer import Viewer

class Pref(Peer):
    Load = Pillow.In
    Add  = Pillow.In

    NoDocument  = Pillow.Out
    SheetNotFound  = Pillow.Out
    Ready = Pillow.OutState

    Receiving = [
        Viewer.In.Document,
        DocumentCache.Out.RequestedDocument,
        DocumentCache.Out.DocumentChanged
    ]

    Sending = [
        DocumentCache.In.RequestDocument,
        Viewer.In.Refresh
    ]

    def isReady(self, ignoreVersion=False):
        if self._configDoc is not None and self._document is not None:
            configRev = self._configDoc.rev()
            docRev = self._document.rev()

            if (configRev == None or configRev != self._configRev) or (docRev == None or docRev != self._docRev) or ignoreVersion:
                self._configRev, self._docRev = configRev, docRev

                from twisted.internet import reactor
                reactor.callLater(0, self._controller.load)

            self._throw(Pref.Out.Ready, True)

        else:
            self._throw(Pref.Out.Ready, False)

    def __init__(self, room, controller, configDocId, path):
        Peer.__init__(self, room)
        self._configDoc = None
        self._path = path

        self._configRev = None
        self._docRev = None

        self._document = None

        self._controller = controller
        self._configDocId = configDocId

        self._catch(Pref.In.Add, self._add)
        self._catch(Viewer.In.Document, self._doc)
        self._catch(DocumentCache.Out.RequestedDocument, self._setConfigDoc)
        self._catch(DocumentCache.Out.DocumentChanged, self._setConfigDoc)

    def updateAll(self):
        self._throw(Viewer.In.Refresh, self._path + ".")

    def _setConfigDoc(self, pillow, doc):
        if not doc or doc.documentID != self._configDocId: return
        self._configDoc = doc
        self.isReady()

    def initialize(self):
        self._throw(DocumentCache.In.RequestDocument, self._configDocId)
        self.isReady()

    def noDocument(self):
        self._throw(Pref.Out.NoDocument, None)

    def notFound(self, name):
        self._throw(Pref.Out.SheetNotFound, name)

    def _doc(self, pillow, doc):
        self._document = doc
        self.isReady()

    def document(self):
        return self._document

    def _add(self, pillow, sheet):
        from twisted.internet import reactor
        reactor.callLater(0, self._controller.createSheet, sheet)

    def configDoc(self):
        return self._configDoc
