# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

class Credentials(Peer):  
    # Request credentials for dynamic peers
    Update     = Pillow.In

    # The requested (or unrequested) credential
    Credential = Pillow.Out
     
    def __init__(self, room):
        Peer.__init__(self, room)
        self._catch(Credentials.In.Update, self._update)

    def _update(self, *args):
        pass

