# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from viewer import Viewer

class DoubleViewer(Viewer):
    def _refresh(self, pillow, path):
        from wallaby.common.pathHelper import SelectionNotSpecified

        if self._path == None: return

        try:
            if Viewer.matchPath(self._path, path, mode=Viewer.OUTER):
                value = 0
                if self._document:
                    value = self._document.get(self._path)
                if value and self._credentials:
                    credential = self._credentials.getFlat(self._path)
                    if credential == None or 'view' in credential or self._path == '_id':
                        self._cb(value)
                else:
                    self._cb(0)
        except SelectionNotSpecified as e:
            self._cb(0.0)
