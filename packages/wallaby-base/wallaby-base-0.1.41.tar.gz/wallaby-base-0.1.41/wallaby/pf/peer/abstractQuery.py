# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

class AbstractQuery(object):
    from wallaby.pf.pillow import Pillow

    __metaclass__ = Pillow
    #Receiving pillows
    Query = Pillow.In

    #Sending pillows
    Result = Pillow.OutState

    def __init__(self, *args):
        self._catch(AbstractQuery.In.Query, self._query)

    def _query(self, pillow, query):
        pass
