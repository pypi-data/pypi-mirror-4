# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

class RoomDebuggerParty(Peer):
    def __init__(self, room):
        Peer.__init__(self, room)

        from roomDebuggerRouting import RoomDebuggerRouting
        from credentialsRouting import CredentialsRouting
        from roomDebugger import RoomDebugger

        #Peers
        self.add(RoomDebuggerRouting(room))
        self.add(CredentialsRouting(room))
        self.add(RoomDebugger(room))
