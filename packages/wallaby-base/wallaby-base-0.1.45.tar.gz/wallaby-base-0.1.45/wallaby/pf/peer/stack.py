# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

class Stack(Peer):
    ShowLayer = Pillow.In
    HideLayer = Pillow.In
    EnableLayer = Pillow.In
    DisableLayer = Pillow.In

    def __init__(self, room, controller):
        Peer.__init__(self, room)
        self._controller = controller
        self._catch(Stack.In.ShowLayer, self._showLayer)
        self._catch(Stack.In.HideLayer, self._hideLayer)
        self._catch(Stack.In.EnableLayer, self._enableLayer)
        self._catch(Stack.In.DisableLayer, self._disableLayer)

    def _showLayer(self, pillow, name):
        self._controller.showLayer(name)

    def _hideLayer(self, pillow, name):
        self._controller.hideLayer(name)

    def _enableLayer(self, pillow, name):
        self._controller.enableLayer(name)

    def _disableLayer(self, pillow, name):
        self._controller.disableLayer(name)
