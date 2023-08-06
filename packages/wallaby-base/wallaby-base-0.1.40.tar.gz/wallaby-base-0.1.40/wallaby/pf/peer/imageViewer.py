# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from viewer import Viewer

class ImageViewer(Viewer):
    def __init__(self, room, cb, path):
        Viewer.__init__(self, room, cb, path)

    def _refresh(self, pillow, path):
        from wallaby.common.pathHelper import SelectionNotSpecified
        from twisted.internet import defer

        if self._path and Viewer.matchPath(self._path, path, mode=Viewer.OUTER):
            d = None

            try:
                if self._document:
                    name = self._document.get(self._path)

                    if name == None: name = self._path

                    if name != None:
                        d = defer.maybeDeferred(self._document.deferredGetAttachment, name)

                if d and self._credentials:
                    credential = self._credentials.getFlat(self._path)
                    if credential == None or 'view' in credential:
                        self._cb(d, name)
                else:
                    d = defer.Deferred()
                    d.callback(None)
                    self._cb(d, None)

            except SelectionNotSpecified as e:
                d = defer.Deferred()
                d.callback(None)
                self._cb(d, None)
