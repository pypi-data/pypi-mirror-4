# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

class Tab(Peer):
    Select = Pillow.In
    SelectByName = Pillow.In

    def __init__(self, room, delegate, path):
        Peer.__init__(self, room)
        self._delegate = delegate
        self._path = path
        self._catch(Tab.In.Select, self._select)
        self._catch(Tab.In.SelectByName, self._selectByName)

    def _select(self, pillow, path):
        name, idx = path.split('.')
        if self._path == name:
            self._delegate.selectByIndex(int(idx))

    def _selectByName(self, pillow, path):
        base, name = path.split('.')
        if self._path == base:
            self._delegate.selectByName(name)
