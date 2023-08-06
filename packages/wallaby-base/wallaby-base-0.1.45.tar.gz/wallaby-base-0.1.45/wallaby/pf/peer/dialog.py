# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

class Dialog(Peer):
    Show = Pillow.In
    Hide = Pillow.In

    def __init__(self, room, dialog):
        Peer.__init__(self, room)
        self._dialog = dialog
        self._catch(Dialog.In.Show, self._show)
        self._catch(Dialog.In.Hide, self._hide)

    def _show(self, *args):
        self._dialog.show()
        self._dialog.raise_()

    def _hide(self, *args):
        self._dialog.hide()
