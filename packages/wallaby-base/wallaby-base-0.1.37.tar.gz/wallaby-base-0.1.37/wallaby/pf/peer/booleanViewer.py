# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from viewer import Viewer

class BooleanViewer(Viewer):
    def _refresh(self, pillow, path):
        from wallaby.common.pathHelper import SelectionNotSpecified

        try:
            if Viewer.matchPath(self._path, path, mode=Viewer.OUTER):
                value = False
                if self._document:
                    value = bool(self._document.get(self._path))
                if value and self._credentials:
                    credential = self._credentials.getFlat(self._path)
                    if credential == None or 'view' in credential or self._path == '_id':
                        self._cb(value)
                else:
                    self._cb(False)
        except SelectionNotSpecified as e:
            self._cb(False)
