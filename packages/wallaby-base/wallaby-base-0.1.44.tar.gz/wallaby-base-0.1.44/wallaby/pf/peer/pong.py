# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

class Pong(Peer):
    #Receiving pillows
    Pong = Pillow.InOut

    def __init__(self, *args):
        Peer.__init__(self, *args)
        self._catch(Pong.In.Pong, self.message)

    def message(self, pillow, feathers):
        self._throw(Pong.Out.Pong, int(feathers)+1);
