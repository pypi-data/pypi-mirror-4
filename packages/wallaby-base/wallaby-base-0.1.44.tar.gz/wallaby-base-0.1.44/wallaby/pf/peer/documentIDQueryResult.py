# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from wallaby.common.queryResult import QueryResult
from twisted.internet import defer
from peer import *
from functools import *

class DocumentIDQueryResult(Peer, QueryResult):
    RequestedDocument = Pillow.In
    RequestDocument = Pillow.Out

    ObjectType = Pillow.Runtime

    def __init__(self, source, query, ids, room, count=None):
        Peer.__init__(self, room)
        QueryResult.__init__(self, source, query)

        self._ids = ids
        self._count = count

        self._catch(DocumentIDQueryResult.In.RequestedDocument, self._requestedDocument)
        self._defers = {}
        self._deferredDocs = {}
        self._orderPath = None

    def setOrderPath(self, path):
        self._orderPath = path

    def deferredGetValue(self, index, path):
        from twisted.internet import reactor

        if index < 0 or index >= self.length():
            d = defer.Deferred()
            reactor.callLater(0, d.callback, None)
            return d
        else:
            documentID = self.getDocumentID(index)

        return self.deferredGetDocValue(documentID, path)

    def getImage(self, row, path, documentID=None):
        if documentID == None:
            documentID = self.getDocumentID(row)

        if isinstance(path, (list, tuple)):
            path = path[0]

        if documentID not in self._deferredDocs:
            self._deferredDocs[documentID] = defer.Deferred()
            self._throw(DocumentIDQueryResult.Out.RequestDocument, documentID)

        d = defer.Deferred()
        self._deferredDocs[documentID].addCallback(partial(self._getImage, path, d))
        return d

    @defer.inlineCallbacks
    def _getImage(self, path, d, doc):
        from wallaby.qt_combat import QtGui, QtCore

        if isinstance(doc, QtGui.QPixmap):
            d.callback(doc)
            defer.returnValue(doc)
            return

        p = QtGui.QPixmap()

        if doc == None:
            d.callback(p)
            return

        data = yield defer.maybeDeferred(doc.deferredGetAttachment, path)

        if data != None:
            img = QtGui.QImage.fromData(data).scaled(128, 128, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            if img != None:
                p.convertFromImage(img)
        d.callback(p)
        defer.returnValue(p)



    def deferredGetDocument(self, index):
        from twisted.internet import reactor

        if index >= self.length() or index < 0:
            d = defer.Deferred()
            reactor.callLater(0, d.callback, None)
            return d

        documentID = self.getDocumentID(index)
        if documentID not in self._deferredDocs[documentID]:
            self._deferredDocs[documentID] = defer.Deferred()
            self._throw(DocumentIDQueryResult.Out.RequestDocument, documentID)

        return self._deferredDocs[documentID]

    def deferredGetDocValue(self, documentID, path):
            if documentID not in self._defers:
                self._defers[documentID] = {}

            if path not in self._defers[documentID]:
                self._throw(DocumentIDQueryResult.Out.RequestDocument, documentID)
                self._defers[documentID][path] = defer.Deferred()

            return self._defers[documentID][path]

    def _chainCallback(self, d, v):
        d.callback(v)
        return v

    def _requestedDocument(self, pillow, document):
        from twisted.internet import reactor
        documentID = document.documentID

        if documentID in self._deferredDocs:
            d = self._deferredDocs[documentID]
            del self._deferredDocs[documentID]
            reactor.callLater(0, d.callback, document)

        if documentID in self._defers:
            for path, d in self._defers[documentID].iteritems():
                if '(' in path:
                    import re
                    newpath = re.sub(r'\([^)]+\)\.', '', path, 1)
                    m = re.match(r'\(([^)]+)\)\.', path)
                    docID = document.get(m.group(1))

                    if docID != None:
                        newDeferred = self.deferredGetDocValue(docID, newpath)

                        from functools import partial
                        newDeferred.addCallback(partial(self._chainCallback, d))
                    else:
                        reactor.callLater(0, d.callback, None)
                else:
                    reactor.callLater(0, d.callback, document.get(path))

            del self._defers[documentID]

    def getDocumentID(self, index):
        if index >= self.length():
            return None
        return self._ids[index]

    def length(self):
        return len(self._ids)
