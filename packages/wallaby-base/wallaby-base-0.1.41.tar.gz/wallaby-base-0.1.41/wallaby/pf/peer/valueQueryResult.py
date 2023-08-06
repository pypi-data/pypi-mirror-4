# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

from wallaby.common.queryResult import QueryResult
from functools import partial

import math, re

class ListOfDeferreds(list):
    pass

class ValueQueryResult(Peer, QueryResult):
    
    RequestedDocument = Pillow.In
    RequestDocument = Pillow.Out
    SaveDocument = Pillow.Out

    SERIAL = 1

    def __init__(self, source, query, values, room, count=None):
        Peer.__init__(self, room)
        QueryResult.__init__(self, source, query)

        from documentChanger import DocumentChanger
        DocumentChanger.reregisterToken(room + "NextOrder", self.nextOrderToken)

        self._values = values

        from uuid import uuid4
        self._ident  = uuid4().hex
        self._count  = count
        self._limit  = -1
        self._serial = unicode(ValueQueryResult.SERIAL)
        self._orderPath = None
        ValueQueryResult.SERIAL += 1

        if query != None:
            limit = query.get('args.limit')
            if limit != None:
                self._limit = int(limit)

        self._catch(ValueQueryResult.In.RequestedDocument, self._requestedDocument)
        self._defers = {}
        self._deferredDocs = {}

    def setOrderPath(self, path):
        self._orderPath = path

    def _loadPartial(self, idx, cb):
        if self._limit == -1:
            d = defer.Deferred()
            d.callback(None)
            return d

        l = len(self._values)

        if idx < l and isinstance(self._values[idx], ListOfDeferreds):
            d = defer.Deferred()
            self._values[idx].append( (d, cb) )
            return d

        # fill all skipped values with None (could be loaded later)
        for i in range(l-1,idx):
            self._values.append(None)

        l = len(self._values)

        # fill with deferred list for later requests 
        for i in range(idx, idx+self._limit):
            if i >= self._count: break
            if i >= l: 
                self._values.append(ListOfDeferreds())
            else:
                if not isinstance(self._values[i], ListOfDeferreds):
                  self._values[i] = ListOfDeferreds()

        d = defer.Deferred()
        self._values[idx].append( (d, cb) )

        from twisted.internet import reactor
        reactor.callLater(0, self.__loadPartial, idx)
        return d


    @defer.inlineCallbacks
    def __loadPartial(self, idx):
        # make copy to support concurrent requests!
        import copy
        query = copy.deepcopy(self.query)
        query.set('args.skip', idx)

        values, cnt = yield self._source.updateQuery(query)
        if cnt >= 0:
            self._count = cnt

        l = len(self._values)

        callList = ListOfDeferreds()

        # fill values to value cache and call waiting deferreds 
        j = 0
        for i in range(idx, idx+self._limit):
            if j >= len(values): break

            if isinstance(self._values[i], ListOfDeferreds):
                for deferredAndCB in self._values[i]:
                    callList.append(deferredAndCB)

            self._values[i] = values[j]
            j += 1

        for d, cb in callList:
            d2 = cb()
            d2.addCallback(d.callback)

    def getImage(self, row, path, documentID=None):
        if documentID == None:
            documentID = self.getDocumentID(row)

        if isinstance(path, (list, tuple)):
            path = path[0]

        if documentID not in self._deferredDocs:
            self._deferredDocs[documentID] = defer.Deferred()
            self._throw(ValueQueryResult.Out.RequestDocument, documentID)

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

    # get value from query result. Load more rows if neccessary 
    def deferredGetValue(self, index, path):
        from twisted.internet import reactor

        if index < 0 or index >= len(self._values) or self._values[index] == None or isinstance(self._values[index], ListOfDeferreds):
            if index < 0 or self._count == None or not self._source or index >= self._count:
                d = defer.Deferred()
                reactor.callLater(0, d.callback, None)
                return d
            else:
                return self._loadPartial(index, partial(self._deferredGetRowValue, index, path))

        return self._deferredGetRowValue(index, path)

    def _deferredGetRowValue(self, index, path):
        documentID = self.getDocumentID(index)

        from wallaby.common.document import Document
        doc = Document(documentID, data=self._values[index])

        return self.deferredGetDocValue(path, documentID, document=doc)

    # get corresponding document for row. Load more rows if neccessary
    def deferredGetDocument(self, index):
        if index < 0 or index >= len(self._values) or self._values[index] == None or isinstance(self._values[index], ListOfDeferreds):
            if index < 0 or self._count == None or not self._source or index >= self._count:
                d = defer.Deferred()
                reactor.callLater(0, d.callback, None)
                return d
            else:
                return self._loadPartial(index, partial(self._deferredGetDocument, index))

        return self._deferredGetDocument(index)

    def reorder(self, row, i1, i2):
        if self._orderPath is None:
            FX.crit("No valid order path")
            return

        d1 = self.deferredGetValue(i1, "key.0")
        d2 = self.deferredGetValue(i2, "key.0")
        d3 = self.deferredGetDocument(row)

        list = defer.DeferredList([d1, d2, d3])
        list.addCallback(partial(self._deferredReorderRows, row, i1, i2))

    @defer.inlineCallbacks
    def _deferredReorderRows(self, row, i1, i2, ((valid1, key1), (valid2, key2), (valid3, doc))):
        if not valid3: 
            FX.crit("Error retrieving document")
            return

        if not valid1 and not valid2:
            FX.crit("No valid orders")
            return

        if valid1 and key1 != None and valid2 and key2 != None:
            if abs(key1 - key2) < 1e-6:
                FX.warn("min-delta reached! Reorder all items")
                doc.set(self._orderPath, (i1 + i2)/2.0)
                docs = [doc]

                for i in range(0, self.length()):
                    if i == row: continue
                    d = yield self.deferredGetDocument(i)
                    d.set(self._orderPath, i)
                    docs.append(d)

                self._throw(ValueQueryResult.Out.SaveDocument, (docs, None))
                return

            doc.set(self._orderPath, (key1 + key2)/2.0)
        elif valid1 and key1 != None:
            doc.set(self._orderPath, math.ceil(key1 + 1.0))
        else: 
            doc.set(self._orderPath, math.floor(key2 - 1.0))

        self._throw(ValueQueryResult.Out.SaveDocument, (doc, None))

    def _deferredGetDocument(self, index):
        documentID = self.getDocumentID(index)
        if documentID not in self._deferredDocs:
            self._deferredDocs[documentID] = defer.Deferred()
            self._throw(ValueQueryResult.Out.RequestDocument, documentID)

        return self._deferredDocs[documentID]

    def deferredGetDocValue(self, path, documentID, document=None):
        if path == None:
            d = defer.Deferred()
            d.callback(None)
            return

        if documentID not in self._defers:
            self._defers[documentID] = {}

        if '(' in path or document==None:
            if path not in self._defers[documentID]:
                self._defers[documentID][path] = defer.Deferred()

                if document != None:
                    from twisted.internet import reactor 
                    reactor.callLater(0, self._requestedDocument, None, document)
                else:
                    self._throw(ValueQueryResult.Out.RequestDocument, documentID)

            return self._defers[documentID][path]
        # Performance boost for existing values 
        else:
            d = defer.Deferred()
            try:
                if '|' in path:
                    pathes = path.split('|')
                    value, i = None, 0
                    while value == None and i < len(pathes):
                        path = pathes[i]
                        value = document.get(path)  
                        i += 1

                    if value == None:
                        d.callback("-")
                    else:
                        d.callback(value)
                else:
                    d.callback(document.get(path))
            except:
                d.callback('-')

            return d

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
            for path, d in self._defers[documentID].items():
                if '|' in path:
                    pathes = path.split('|')
                else:
                    pathes = [path]

                value, i = None, 0
                while value == None and i < len(pathes):
                    path = pathes[i]

                    if '(' in path:
                        newpath = re.sub(r'\([^)]+\)\.', '', path, 1)
                        m = re.match(r'\(([^)]+)\)\.', path)
                        docID = document.get(m.group(1))

                        if docID != None:
                            newDeferred = self.deferredGetDocValue(newpath, docID)
                            newDeferred.addCallback(partial(self._chainCallback, d)) 
                        else:
                            reactor.callLater(0, d.callback, None)

                        del self._defers[documentID]
                        return
                    else:
                        if '_source' in document._data and "_source" not in path:
                            value = document.get('_source.' + path)
                        else:
                            value = document.get(path)

                    i += 1

                reactor.callLater(0, d.callback, value)

            del self._defers[documentID]

    def getDocumentID(self, index):
        if self._values == None or index >= len(self._values):
            # Dummy documentID for table model expansion
            return self._serial + "_" + unicode(index)

        try:
            if 'value' in self._values[index] and isinstance(self._values[index]['value'], dict) and '_id' in self._values[index]['value']:
                return self._values[index]['value']['_id']
        except Exception as e:
            print "Exception:", self._values[index], self.query._data, e

        if '_id' in self._values[index]:
            return self._values[index]['_id']

        if 'id' in self._values[index]:
            return self._values[index]['id']

        return self._ident + str(index)

    @defer.inlineCallbacks
    def nextOrderToken(self, doc):
        if self._values != None and self._orderPath != None:
            order = yield self.deferredGetValue(self.length()-1, "key.0")
            defer.returnValue(order+1)
            return

        defer.returnValue(self.length())

    def length(self):
        if self._count != None:
            return self._count
        else:
            return len(self._values)
