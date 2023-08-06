# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from uiPeer import *

from wallaby.common.pathHelper import SelectionNotSpecified, PathHelper
from viewer import Viewer
from editor import Editor

class EmbeddedViewer(UIPeer):
    Add = Pillow.In
    Remove = Pillow.In
    Select = Pillow.In
    SelectionChanged = Pillow.Out

    Up = Pillow.In
    Down = Pillow.In

    LIST = 1
    DICT = 2

    def __init__(self, room, path, delegate, conflictCB=None, isList=True, wrapInList=False, identifier=None):
        UIPeer.__init__(self, room, path)

        self._delegate = delegate
        self._document = None
        self._enabled  = False
        self._conflictCB = conflictCB
        self._isList = isList
        self._wrapInList = wrapInList
        self._identifier = identifier

        self._catch(Viewer.In.Document, self._setDocument)
        self._catch(Viewer.In.Refresh, self._refresh)
        self._catch(Editor.In.Enable, self._enable)
        self._catch(EmbeddedViewer.In.Add, self._add)
        self._catch(EmbeddedViewer.In.Remove, self._remove)
        self._catch(EmbeddedViewer.In.Select, self._select)

        self._catch(EmbeddedViewer.In.Up, self._up)
        self._catch(EmbeddedViewer.In.Down, self._down)

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

    def _newCredentials(self, pillow, feathers):
        UIPeer._newCredentials(self, pillow, feathers)
        self._refresh(pillow, self._path)

    def _up(self, pillow, path):
        if not self._enabled: return

        if self._identifier != None:
            if not path.startswith(self._identifier):
                return

            path = path.replace(self._identifier + ":", "")

        if path != self._path: return
        if not self._isList:
            FX.crit("Moving not supported for dictionary viewer")
            return

        data = self._document.get(self._path, asList=True, wrap=self._wrapInList)
        if data == None: return

        sel = PathHelper.getValue(self._document.selection, self._path + '.*._selection')
        if sel == None or sel == 0: return

        data[sel-1], data[sel] = data[sel], data[sel-1] 

        if self._delegate: self._delegate.changedCB()
        self._document.select(self._path + '.*', sel-1) 
        if self._delegate: self._delegate.selectRow(sel-1)

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

    def _down(self, pillow, path):
        if not self._enabled: return

        if self._identifier != None:
            if not path.startswith(self._identifier):
                return

            path = path.replace(self._identifier + ":", "")

        if path != self._path: return

        if not self._isList:
            FX.crit("Moving not supported for dictionary viewer")
            return

        data = self._document.get(self._path, asList=True, wrap=self._wrapInList)
        if data == None: return

        sel = PathHelper.getValue(self._document.selection, self._path + '.*._selection')
        if sel == None or sel == len(data)-1: return

        data[sel], data[sel+1] = data[sel+1], data[sel] 

        if self._delegate: self._delegate.changedCB()
        self._document.select(self._path + '.*', sel+1) 
        if self._delegate: self._delegate.selectRow(sel+1)

    def _remove(self, pillow, path):
        if not self._enabled: return

        if self._identifier != None:
            if not path.startswith(self._identifier):
                return

            path = path.replace(self._identifier + ":", "")

        if path != self._path: 
            return

        if self._isList:
            data = self._document.get(self._path, asList=True, wrap=self._wrapInList)
        else:
            data = self._document.get(self._path, asDict=True)

        sel = PathHelper.getValue(self._document.selection, self._path + '.*._selection')
        if self._delegate and sel != None:
            row = self._delegate.getRow(sel)
            self._delegate.beginDeleteCB(row)
            del data[sel]
            self._delegate.endDeleteCB(row)

            if row >= len(data):
                row = len(data) - 1

            if row < 0:
                sel = None
            else:
                sel = self._delegate.getKey(row)

            if len(data) == 0:
                self._document.select(self._path + '.*', None) 
            else:
                self._document.select(self._path + '.*', sel)
                if self._delegate: self._delegate.selectRow(sel)

            self._throw(Editor.Out.FieldChanged, Editor.translatePath(self._document, self._path + '.*'))

    def _add(self, pillow, path):
        if not self._enabled: return

        doc = None

        if self._identifier != None:
            if not path.startswith(self._identifier):
                return

            path = path.replace(self._identifier + ":", "")

        if isinstance(path, tuple) or isinstance(path, list):
            path, doc = path

        if path != self._path: 
            return

        try:
            if self._isList:
                data = self._document.get(self._path, asList=True, wrap=self._wrapInList)
            else:
                data = self._document.get(self._path, asDict=True)
        except Exception as e:
            return

        if data == None:
            if self._isList:
                data = []
            else:
                data = {}

            try:
                self._document.set(self._path, data)
                if self._delegate != None:
                    self._delegate.dataCB(data)
            except Exception as e:
                return

        try:
            sel = PathHelper.getValue(self._document.selection, self._path + '.*._selection')
        except SelectionNotSpecified:
            sel = None

        if sel == None:
            if self._isList:
                sel = len(data)
            else:
                sel = "__new__"

        row = self._delegate.getRow(sel)
        if self._delegate: self._delegate.beginInsertCB(row)

        if self._isList:
            data.insert(sel, doc)
        else:
            data['__new__'] = doc

        if self._delegate: self._delegate.endInsertCB(row)

        self._document.select(self._path + '.*', sel) 
        if self._delegate: self._delegate.selectRow(sel)

        self._throw(Editor.Out.FieldChanged, Editor.translatePath(self._document, self._path + '.*'))

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

        # if self._document:
        #     self._document.select(self._path + '.*', idx)

        #     path = self._path + ".*"
        #     path = path.replace('__root__.', '')
        #     self._throw(EmbeddedViewer.Out.SelectionChanged, path)
        #     # self._throw(EmbeddedViewer.Out.SelectionChanged, Editor.translatePath(self._document, path))

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
