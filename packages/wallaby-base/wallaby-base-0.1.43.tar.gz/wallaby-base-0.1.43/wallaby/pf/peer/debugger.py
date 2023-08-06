# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

class Debugger(Peer):
    from wallaby.pf.room import Room 

    Receiving = [
        Room.Out.NoHandlerFound
    ]

    def __init__(self, room, pillow=Room.Out.NoHandlerFound, notFoundLimit=5):
        Peer.__init__(self, room)
        self._roomName = room
        self._catch(pillow, self._message, passThrower=True)
        self._notFoundLimit = notFoundLimit

        self._notFound = {}

    def color(self, this_color, string):
        return "\033[" + this_color + "m" + string + "\033[0m"

    def _message(self, pillow, feather, thrower=None):
        from wallaby.pf.room import Room
        if self._notFoundLimit > 0 and pillow == Room.Out.NoHandlerFound and feather in self._notFound and self._notFound[feather] == self._notFoundLimit: return

        thrower = str(thrower)
        if '.' in thrower:
            import re
            match = re.match('<([^\s]+)', thrower)
            thrower = match.group(1).split('.')
            thrower = thrower[-2] + "." + thrower[-1]

        out = "|{0:<16}|{1:<48}|{2:<64}|{3}".format(self._roomName,thrower,pillow,feather)

        if pillow == Room.Out.NoHandlerFound:
            if feather not in self._notFound:
                self._notFound[feather] = 1
            else:
                self._notFound[feather] += 1

            if self._notFound[feather] == self._notFoundLimit:
                out += "..."

            out = self.color('1;31', out)

        import wallaby.FX as FX
        FX.debug(out)
