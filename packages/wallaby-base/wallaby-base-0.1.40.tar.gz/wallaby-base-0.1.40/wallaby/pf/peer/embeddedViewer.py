# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from uiPeer import *

from wallaby.common.pathHelper import SelectionNotSpecified, PathHelper
from viewer import Viewer
from editor import Editor
from documentChanger import DocumentChanger

class EmbeddedViewer(UIPeer):
    Select = Pillow.In

    LIST = 1
    DICT = 2

    def __init__(self, room, path, delegate, conflictCB=None, isList=True, wrapInList=False, identifier=None, editOnInsert=False):
        UIPeer.__init__(self, room, path)

        self._delegate = delegate
        self._document = None
        self._enabled  = False
        self._conflictCB = conflictCB
        self._isList = isList
        self._wrapInList = wrapInList
        self._identifier = identifier

        self._inserted = None

        if editOnInsert:
            self._catch(DocumentChanger.Out.RowInserted, self._rowInserted)

        self._catch(Viewer.In.Document, self._setDocument)
        self._catch(Viewer.In.Refresh, self._refresh)
        self._catch(Editor.In.Enable, self._enable)
        self._catch(EmbeddedViewer.In.Select, self._select)

        self._catch(Editor.In.Conflict, self._conflict)
        self._resolved = False

    def resolve(self, data=None, **ka):
        if len(ka) > 0:
            self._document.resolve(**ka)
            self._throw(Viewer.In.Refresh, "")
        elif data != None:
            self._document.set(self._path, data)
            self._throw(Viewer.In.Refresh, self._path)
    
        self._resolved = True

    def hasImage(self, name):
        return self._document.hasAttachment(name)

    def getImage(self, name):
        return defer.maybeDeferred(self._document.deferredGetAttachment, name)

    def _select(self, pillow, (path, idx) ):
        if self._identifier != None:
            if not path.startswith(self._identifier):
                return

            path = path.replace(self._identifier + ":", "")

        if path != self._path: return
 
        if self._delegate:
            self._delegate.selectRow(idx)

    def fieldChanged(self, key, field):
        path = self._path + "." + unicode(key)
        path = path.replace('__root__.', '')

        if field == "*":
            self._throw(Editor.Out.FieldChanged, Editor.translatePath(self._document, path))
        else:
            self._throw(Editor.Out.FieldChanged, Editor.translatePath(self._document, path + "." + field))

    def dataChanged(self, sel):
        path = self._path + ".*"
        path = path.replace('__root__.', '')

        self._throw(Editor.Out.FieldChanged, Editor.translatePath(self._document, path))

        self._document.select(self._path + '.*', sel) 
        if self._delegate: self._delegate.selectRow(sel)

    def _enable(self, pillow, isEnabled):
        self._enabled = isEnabled

    def select(self, idx):
        if self._document:
            try:
                currentIdx = PathHelper.getValue(self._document.selection, self._path + '.*._selection') 
                # already selected
                if currentIdx == idx: return 

            except: pass

        from documentChanger import DocumentChanger
        self._throw(DocumentChanger.In.Select, (self._path, idx))

    def _rowInserted(self, pillow, (path, key)):
        if self._path is None or self._delegate is None:
            return

        if Viewer.matchPath(self._path, path, mode=Viewer.OUTER):
            self._inserted = key

    def _refresh(self, pillow, path):
        if self._path is None:
            return
        try:
            # selection changed!
            if path == self._path + ".*":
                try:
                    idx = PathHelper.getValue(self._document.selection, path + '._selection') 
                    if self._delegate:
                        self._delegate.selectRow(idx)
                except: pass

            elif Viewer.matchPath(self._path, path, mode=Viewer.OUTER):
                value = None
                if self._document:
                    if self._isList:
                        value = self._document.get(self._path, asList=True, wrap=self._wrapInList)
                    else:
                        value = self._document.get(self._path, asDict=True)

                if value and self._credentials:
                    credential = self._credentials.getFlat(self._path)
                    if credential == None or 'view' in credential or self._path == '_id':
                        if self._delegate: self._delegate.dataCB(value)
                        if not self._resolved:  
                            if self._document.hasConflicts():
                                d = self._document.loadConflicts()
                                d.addCallback(self._conflictsArrived)
                            else:
                                self._noConflict()

                        if self._delegate and self._inserted != None:
                            self._delegate.editRow(self._inserted)
                else:
                    if self._delegate: self._delegate.dataCB(None)

                if self._document != None and self._document.selection != None:
                    # FIXME: Should we clear the selection here
                    # if "*" in self._path:
                    #     self._document.select(self._path, None)

                    sel = PathHelper.getValue(self._document.selection, self._path + '.*._selection')
                    if sel != None and self._delegate != None: self._delegate.selectRow(sel)

            elif Viewer.matchPath(self._path, path, mode=Viewer.INNER):
                if self._delegate: self._delegate.changedCB()

        except SelectionNotSpecified as e:
            self._delegate.dataCB(None)

        self._inserted = None

    def _conflictsArrived(self, conflicts):
        if conflicts == None: 
            self._noConflict()
            return

        self._resolved = False
        self._conflict(None, conflicts)

    def _noConflict(self):
        if self._conflictCB:
            self._conflictCB(False, None, None)

    def _conflict(self, pillow, feathers): 
        if self._conflictCB: 
            conflicts = [] 

            value = self._document.get(self._path)
 
            if isinstance(feathers, list): 
                for conflict in feathers: 
                    user = conflict.get("wallabyUser")
                    conflicts.append((user, conflict.get(self._path))) 
            else: 
                user = feathers.get("wallabyUser")
                conflictValue = feathers.get(self._path)

                import json
                jsonString = json.dumps(conflictValue)
                jsonString2 = json.dumps(value)

                if jsonString != jsonString2:
                    conflicts.append((user, feathers.get(self._path))) 
         
            if len(conflicts) > 0: 
                self._conflictCB(True, value, conflicts) 
            else: 
                self._conflictCB(False, value, None)

    def _setDocument(self, pillow, document):
        self._document = document
        self._resolved = False
        self._refresh(pillow, self._path)
