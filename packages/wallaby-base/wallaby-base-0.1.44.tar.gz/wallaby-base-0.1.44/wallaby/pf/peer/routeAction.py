# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import Peer

class RouteAction(Peer):
    
    def __init__(self, srcRoom, dstRoom, pillow):
        Peer.__init__(self, srcRoom)
        
        from wallaby.pf.room import House
        self._dstRoom = House.get(dstRoom)

        self._catch(pillow, self._message)

    def _message(self, *args):
        self._dstRoom.throw(*args)
