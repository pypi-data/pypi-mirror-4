# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

class PingPong(Peer):
    from ping import Ping
    from pong import Pong

    Routings = [
        (Ping.Out.Ping, Pong.In.Pong),
        (Pong.Out.Pong, Ping.In.Ping)
    ]

    def __init__(self, room): Peer.__init__(self, room)
