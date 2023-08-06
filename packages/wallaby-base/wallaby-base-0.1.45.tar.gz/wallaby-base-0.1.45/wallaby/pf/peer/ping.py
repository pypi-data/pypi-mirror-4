# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

class Ping(Peer):
    Ping = Pillow.InOut

    def __init__(self, *args):
        Peer.__init__(self, *args)
        self._catch(Ping.In.Ping, self.message)

    def message(self, pillow, feathers):
        self._throw(Ping.Out.Ping, int(feathers)+1);
