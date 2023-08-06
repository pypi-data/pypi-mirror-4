# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

class EnableDocument(Peer):
    from editDocument import EditDocument
    from enabler import Enabler

    Routings = [
        (EditDocument.Out.State, Enabler.In.Enable)
    ]

    def __init__(self, room):
        Peer.__init__(self, room)
