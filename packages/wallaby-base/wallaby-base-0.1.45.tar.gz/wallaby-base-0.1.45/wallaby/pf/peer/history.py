# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

from viewer import *
from editor import *
import copy

from wallaby.common.document import *

class History(Peer):
    Back = Pillow.In
    Forward = Pillow.In

    Receiving = [
        Viewer.In.Document,
        Editor.Out.FieldChanged
    ]

    Sending = [
        Editor.Out.FieldChanged
    ]

    def __init__(self, name):
        Peer.__init__(self, name)

        self._queue = []
        self._fqueue = []
        self._doc = None
        self._lastDoc = None

        self._ignore = False
   
        self._catch(Viewer.In.Document, self._newDoc)
        self._catch(Editor.Out.FieldChanged, self._change)
        self._catch(History.In.Back, self._back)
        self._catch(History.In.Forward, self._forward)

    def _back(self, *args):
        if len(self._queue) == 0: return

        path, value = self._queue.pop()        

        oldVal = self._doc.get(path)
        self._fqueue.append( (path, oldVal) )

        self._lastDoc = Document(data=copy.deepcopy(self._doc._data))

        self._doc.set(path, value)
        self._ignore = True
        self._throw(Editor.Out.FieldChanged, path)

    def _forward(self, *args):
        if len(self._fqueue) == 0: return

        path, value = self._fqueue.pop()
        oldVal = self._doc.get(path)
        self._queue.append( (path, oldVal) )

        self._lastDoc = Document(data=copy.deepcopy(self._doc._data))

        self._doc.set(path, value)
        self._ignore = True
        self._throw(Editor.Out.FieldChanged, path)

    def _newDoc(self, pillow, doc):
        self._doc = doc
        self._lastDoc = Document(data=copy.deepcopy(self._doc._data))

    def _change(self, pillow, path):
        if None in (self._doc, self._lastDoc): return

        if self._ignore: 
            self._ignore = False
            return

        self._queue.append( (path, self._lastDoc.get(path)) )
        self._lastDoc.set(path, self._doc.get(path))

        self._fqueue = []
