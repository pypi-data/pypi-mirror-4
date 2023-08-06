# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from uiPeer import *

class Viewer(UIPeer):
    Refresh = Pillow.In
    RefreshDone = Pillow.InState
    Document = Pillow.InState

    OUTER = 1
    INNER = 2 
    BOTH  = 3
    EXACT  = 4

    def __init__(self, room, cb, path, raw=False, refreshDoneCallback=None, exact=False, ignoreCredentials=False):
        UIPeer.__init__(self, room, path)
        self._valueCB = cb
        self._document = None

        self._exact = exact
        self._ignoreCredentials = ignoreCredentials
        self._raw = raw

        self._refreshDoneCallback = refreshDoneCallback

        self._catch(Viewer.In.Refresh, self._refresh)
        self._catch(Viewer.In.RefreshDone, self._refreshDone)
        self._catch(Viewer.In.Document, self._setDocument)

    @staticmethod
    def matchPath(path, changedPath, mode=3):
        if changedPath == None or path == None: return True

        if mode == Viewer.EXACT:
           if "*" in path:
                leftTokens  = path.split(".")
                rightTokens = changedPath.split(".")

                if len(rightTokens) == len(leftTokens): 
                    match = True

                    for i in range(min(len(leftTokens), len(rightTokens))):
                        if leftTokens[i] == "*": continue
                        if leftTokens[i] != rightTokens[i]: match = False

                    if match: return True
           elif path == changedPath: return True
           return False

        if mode in (Viewer.OUTER, Viewer.BOTH):
            if "*" in path:
                leftTokens  = path.split(".")
                rightTokens = changedPath.split(".")

                if len(rightTokens) <= len(leftTokens): 
                    match = True

                    for i in range(min(len(leftTokens), len(rightTokens))):
                        if leftTokens[i] == "*": continue
                        if leftTokens[i] != rightTokens[i]: match = False

                    if match: return True
            elif path.startswith(changedPath): return True

        if mode in (Viewer.INNER, Viewer.BOTH):
            if "*" in path:
                leftTokens  = path.split(".")
                rightTokens = changedPath.split(".")

                if len(leftTokens) <= len(rightTokens): 
                    match = True
    
                    for i in range(min(len(leftTokens), len(rightTokens))):
                        if leftTokens[i] == "*": continue
                        if leftTokens[i] != rightTokens[i]: match = False

                    if match: return True
            elif changedPath.startswith(path): return True

        return False

    def _cb(self, *args, **ka):
        if self._valueCB != None:
            self._valueCB(*args, **ka)

    def _refreshDone(self, pillow, path):
        if self._refreshDoneCallback:
            self._refreshDoneCallback()

    def selection(self):
        try:
            if self._document is not None: return self._document.getSelection(self._path)
        except: pass
        return None

    def _refresh(self, pillow, path):
        from wallaby.common.pathHelper import SelectionNotSpecified

        if self.destroyed: return

        if self._path == None:
            return

        if path == None:
            if self._raw:
                self._cb(None)
            else:
                self._cb('')
            return

        if self._exact and not Viewer.matchPath(self._path, path, mode=Viewer.EXACT): return
        elif self._raw and not Viewer.matchPath(self._path, path): return
        elif not self._raw and not Viewer.matchPath(self._path, path, mode=Viewer.OUTER): return

        try:
            value = None
            if self._document:
                value = self._document.get(self._path)


            if value != None and self._credentials:
                credential = self._credentials.getFlat(self._path)
                if self._path == '_id' or credential == None or 'view' in credential:
                    if self._raw:
                        self._cb(value)
                    else:
                        uvalue = unicode(value)
                        self._cb(uvalue)
            elif value != None and self._ignoreCredentials:
                if self._raw:
                    self._cb(value)
                else:
                    uvalue = unicode(value)
                    self._cb(uvalue)
            else:
                if self._raw:
                    self._cb(None)
                else:
                    self._cb('')
        except SelectionNotSpecified as e:
            if self._raw:
                self._cb(None)
            else:
                self._cb('-')
        except Exception as e:
            if self._raw:
                self._cb(None)
            else:
                self._cb('Invalid value')

    def _setDocument(self, pillow, document):
        if self.destroyed: return

        self._document = document
        self._refresh(pillow, self._path)

    def document(self):
        return self._document
