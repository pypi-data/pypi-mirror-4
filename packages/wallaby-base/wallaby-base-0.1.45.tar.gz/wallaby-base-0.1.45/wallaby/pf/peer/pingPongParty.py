# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

class PingPongParty(Peer):
    def __init__(self, room):
        Peer.__init__(self, room)

        from pingPong import PingPong
        from ping import Ping
        from pong import Pong

        #Peers
        PingPong(room)

        Ping(room)
        Pong(room)
