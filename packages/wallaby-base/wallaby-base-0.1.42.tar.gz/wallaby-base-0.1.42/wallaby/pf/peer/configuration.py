# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

class Configuration(Peer):
    Configuration = Pillow.In

    def __init__(self, cb):
        Peer.__init__(self, '__CONFIG__')
        self._cb = cb

        self._catch(Configuration.In.Configuration, self._config)

    def _config(self, pillow, document):
        if self._cb != None:
            self._cb(document)
