# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from uiPeer import *

from wallaby.common.pathHelper import SelectionNotSpecified
from viewer import Viewer

class Editor(UIPeer):

    Enable   = Pillow.InState
    Conflict = Pillow.In

    FieldChanged = Pillow.Out

    def __init__(self, room, registerFieldChangedCallback=None, valueCallback=None, setReadOnlyCallback=None, conflictCallback=None, path=None, selectOnEdit=False, selectCallback=None, raw=False, refreshDoneCallback=None):
        UIPeer.__init__(self, room, path)

        self._valueCallback = valueCallback
        self._setReadOnlyCallback = setReadOnlyCallback
        self._conflictCallback = conflictCallback
        self._selectOnEdit = selectOnEdit
        self._selectCallback = selectCallback
        self._refreshDoneCallback = refreshDoneCallback
        self._document = None
        self._readonly = True
        self._isReadOnly = True
        self._raw = raw

        self._catch(Viewer.In.Document, self._setDocument)
        self._catch(Editor.In.Enable, self._setEnabled)
        self._catch(Editor.In.Conflict, self._conflict)
        self._catch(Viewer.In.Refresh, self._refresh)
        self._catch(Viewer.In.RefreshDone, self._refreshDone)

        self._resolved = False

        if registerFieldChangedCallback:
            registerFieldChangedCallback(self._fieldChanged)

    def _setDocument(self, pillow, feathers):
        self._document = feathers
        self._resolved = False
        self._refresh(None, self._path)

    def _resolve(self, **ka):
        if len(ka) > 0:
            self._document.resolve(**ka)
            self._throw(Viewer.In.Refresh, "")

        self._resolved = True

    def isReadOnly(self):
        return self._isReadOnly

    def _setReadOnly(self, ro):
        if ro != self._isReadOnly and not ro and self._selectOnEdit and self._selectCallback != None:
            self._selectCallback()

        self._isReadOnly = ro

        if self._setReadOnlyCallback:
            self._setReadOnlyCallback(ro)

    def _refreshDone(self, pillow, path):
        if self._refreshDoneCallback:
            self._refreshDoneCallback()

    def _refresh(self, pillow, path):
        if self.destroyed: return

        if path == None or self._readonly:
            self._setReadOnly(True)
            self._noConflict()
            return

        if self._document:
            try:
                if Viewer.matchPath(self._path, path, mode=Viewer.OUTER):
                    self._document.get(self._path)

                    if self._credentials:
                        credential = self._credentials.getFlat(self._path)
                        if credential == None or 'edit' in credential: #Hide whole widget
                            self._setReadOnly(self._readonly)
                            if not self._resolved:
                                if self._document.hasConflicts():
                                    d = self._document.loadConflicts()
                                    d.addCallback(self._conflictsArrived)
                                else:
                                    self._noConflict()

            except SelectionNotSpecified as e:
                self._setReadOnly(True)
        else:
            self._setReadOnly(True)

    def _conflictsArrived(self, conflicts):
        if conflicts == None: 
            self._noConflict()
            return

        self._resolved = False

        self._conflict(None, conflicts)

    def _setEnabled(self, pillow, enabled):
        self._readonly = not enabled
        self._refresh(None, self._path)

    def _noConflict(self):
        if self._conflictCallback:
            self._conflictCallback(False, None, None)

    def _conflict(self, pillow, payload):
        if '*' in self._path: return

        if self._conflictCallback:
            value = self._document.get(self._path)
            conflicts = []

            if isinstance(payload, list):
                for conflict in payload:
                    conflictValue = conflict.get(self._path)
                    user = conflict.get("wallabyUser")
                    if conflictValue != value: conflicts.append((user, conflictValue))
            else:
                conflictValue = payload.get(self._path)
                user = payload.get("wallabyUser")
                if conflictValue != value: conflicts.append((user, conflictValue))
        
            if len(conflicts) > 0:
                self._conflictCallback(True, value, conflicts)
            else:
                self._conflictCallback(False, value, None)

    def changeValue(self, value):
        if self._readonly: return

        if (self._document):
            try:
                if self._document.get(self._path) != value:
                    self._document.set(self._path, value) 
                    self._throwFieldChanged(self._path)
            except SelectionNotSpecified as e:
                self._setReadOnly(True)

    @staticmethod
    def translatePath(doc, path):
        if doc != None and "*" in path:
            try:
                trans = doc.getSelection(path)
                return trans
            except:
                return None
        else:
            return path

    def _throwFieldChanged(self, path):
        self._throw(Editor.Out.FieldChanged, Editor.translatePath(self._document, path))

    def _fieldChanged(self):
        if self.destroyed: return

        value = None
        if self._valueCallback:
            if self._raw:
                value = self._valueCallback()
            else:
                oldValue = None
                try:
                    oldValue = self._document.get(self._path)
                except:
                    pass

                if oldValue == None or isinstance(oldValue, str) or isinstance(oldValue, unicode):
                    value = unicode(self._valueCallback())
                else:
                    value = self._valueCallback()

                    if isinstance(value, float) or isinstance(oldValue, float):
                        value = float(value)

                    elif isinstance(oldValue, int) or isinstance(value, int):
                        value = int(value) 
                    
                    else:
                        value = unicode(self._valueCallback())

        self.changeValue(value)
