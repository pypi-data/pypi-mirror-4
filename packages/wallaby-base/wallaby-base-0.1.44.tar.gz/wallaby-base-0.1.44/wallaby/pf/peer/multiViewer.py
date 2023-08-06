# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from uiPeer import *

from wallaby.common.queryDocument import QueryDocument
from documentCache import DocumentCache

class MultiViewer(UIPeer):

    Data = Pillow.InState
    DataChanged = Pillow.In
    Refresh = Pillow.In
    ClearSelection = Pillow.In
    SelectID = Pillow.In

    Select = Pillow.Out
    MultiSelect = Pillow.Out
    Query  = Pillow.OutState
    QueryDocument = Pillow.OutState

    ObjectType = Pillow.Runtime

    def __init__(self, room=None, view=None, viewIdentifier=None, viewArguments=None, dataView=None, delegate=None, autoUpdate=True, orderPath=None, queryDocID=None, **ka):
        UIPeer.__init__(self, room)
        self._delegate    = delegate

        self._view           = view
        self._viewIdentifier = viewIdentifier
        self._viewArguments  = viewArguments
        self._dataView       = dataView
        self._orderPath      = orderPath
        self._queryDocID     = queryDocID

        self._autoUpdate = autoUpdate

        self._queryResult = None
        self._nextQueryResult = None
        # self._initialized = False

        if self._queryDocID != None and len(self._queryDocID) > 0:
            self._catch(DocumentCache.Out.RequestedDocument, self._queryDocArrived)
            self._queryDocument = None
        else:
            self._queryDocument = QueryDocument({
                    'view': self._view,
                    'postfix': '',
                    'identifier': self._viewIdentifier,
                    'dataView': self._dataView,
                    'args': self._viewArguments
            })

        self._catch(MultiViewer.In.Data, self._refreshData)
        self._catch(MultiViewer.In.DataChanged, self._updateData)
        self._catch(MultiViewer.In.Refresh, self._updateQuery)
        self._catch(MultiViewer.In.ClearSelection, self._clearSelection)
        self._catch(MultiViewer.In.SelectID, self._selectID)

    def getImage(self, *args, **ka):
        if not self._queryResult: 
            d = defer.Deferred()
            d.callback(None)
            return d

        return self._queryResult.getImage(*args, **ka)
 

    def sort(self, field, order):
        if not self._queryDocument: return

        if self._queryDocument.get("args") != None:
            if field == '__default__':
                self._queryDocument.set('postfix', '')
            else:
                self._queryDocument.set('postfix', 'By' + field.capitalize())
    
            self._queryDocument.set('args.sort', field)
    
            desc  = self._queryDocument.get('args.descending')
            start = self._queryDocument.get('args.startkey')
            end   = self._queryDocument.get('args.endkey')
            if desc == None: desc = False
    
            if order == 0:
                self._queryDocument.set('args.descending', False)
                if desc and start != None and end != None:
                    self._queryDocument.set('args.startkey', end)
                    self._queryDocument.set('args.endkey', start)
    
            else:
                self._queryDocument.set('args.descending', True)
                if not desc and start != None and end != None:
                    self._queryDocument.set('args.startkey', end)
                    self._queryDocument.set('args.endkey', start)
        else:
            sort = self._queryDocument.get("sort")
            if sort == None or len(sort) == 0: 
                sort = [{field:{"order": None}}]
                self._queryDocument.set("sort", sort)
            elif field not in sort[0]:
                sort[0] = {field:{"order": None}}

            if isinstance(sort[0][field], dict):
                if order == 0:
                    sort[0][field]["order"] = "asc"
                else:
                    sort[0][field]["order"] = "desc"
            else:
                if order == 0:
                    sort[0][field] = "asc"
                else:
                    sort[0][field] = "desc"

        self._updateQuery()

    def initialize(self):
        if self._queryDocID is not None and len(self._queryDocID) > 0:
            self._throw(DocumentCache.In.RequestDocument, self._queryDocID)
        else:
            self._queryDocArrived(None, self._queryDocument)

    def _queryDocArrived(self, pillow, doc):
        if doc == None: return
        if doc != self._queryDocument and doc.documentID != self._queryDocID: return

        self._queryDocument = doc

        if self._viewIdentifier != None:
            viewRoom = self._viewIdentifier.upper()
            self._throw(viewRoom + ':' + MultiViewer.Out.QueryDocument, self._queryDocument)

        if self._autoUpdate:
            self._updateQuery()

    def _clearSelection(self, pillow, feathers):
        self._delegate.clearSelection()

    def _selectID(self, pillow, id):
        if not self._queryResult: return

        for i in range(self.length()):
            if id == self._queryResult.getDocumentID(i):
                self._delegate.selectRow(i)

    def doMultiSelect(self, selection):
        ids = [] 
        for s in selection:
            if s != None and s < self.length():
                ids.append(self._queryResult.getDocumentID(s))

        self._throw(MultiViewer.Out.MultiSelect, ids)

    def doSelect(self, idx, tab):
        if idx == None:
            self._throw(MultiViewer.Out.Select, (None, None, None))
        else:
            self._throw(MultiViewer.Out.Select, (self._queryResult.getDocumentID(idx), tab, idx))

    def _updateQuery(self, pillow=None, feathers=None):
        self._throw(MultiViewer.Out.Query, self._queryDocument)

    def length(self):
        if self._queryResult == None:
            return 0
        else:
            l = self._queryResult.length()
            if l <= 0:
                return 0
            else:
                return l

    def deferredGetValue(self, row, path):
        if self._queryResult == None: return None
        return self._queryResult.deferredGetValue(row, path)

    def reorder(self, *args):
        if self._queryResult == None: return None
        return self._queryResult.reorder(*args)

    def deferredGetDocument(self, row):
        if self._queryResult == None: return None
        return self._queryResult.deferredGetDocument(row)

    def _doRefreshData(self, queryResult):
        if self._delegate != None:
            self._delegate.dataCB(queryResult)

    def _updateData(self, pillow, document):
        if self._delegate != None:
            self._delegate.changedCB(document.documentID)

    def _refresh(self, pillow, path):
        self._refreshData(pillow, self._nextQueryResult)

    def _refreshData(self, pillow, queryResult):
        if queryResult == None:
            self._doRefreshData(None)
            return

        if queryResult.identifier() == None or queryResult.identifier() == self._viewIdentifier:
            initialData = False

            self._nextQueryResult = queryResult

            if self._queryResult == None and queryResult != None:
                initialData = True

            if self._credentials:
                self._queryResult = queryResult
                self._queryResult.setOrderPath(self._orderPath)

                credential = self._credentials.getFlat("VIEW." + unicode(self._viewIdentifier))
                if credential == None or 'view' in credential: #TODO: Hide whole widget
                    self._doRefreshData(queryResult)
                    if initialData and self._delegate:
                        from twisted.internet import reactor
                        reactor.callLater(0.3, self._delegate.initialData)
            else:
                self._doRefreshData(None)


