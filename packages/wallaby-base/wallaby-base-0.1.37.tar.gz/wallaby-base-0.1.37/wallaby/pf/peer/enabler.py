# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

class Enabler(Peer):
    Enable = Pillow.InState

    def __init__(self, room, cb, feathers):
        Peer.__init__(self, room)
        self._cb = cb
        self._feathers = {}
        self._otherFeathers = {}

        self._enabled = {}

        self._negate = False
        self._negateOther = {}

        if feathers is None: return

        for p in feathers:
            if p is None: continue
            if ':' in p:
                room, p = p.split(':')
                if room not in self._otherFeathers: self._otherFeathers[room] = {}

                if p.startswith('!'):
                    p = p[1:]
                    self._negateOther[room] = True
                else:
                    self._negateOther[room] = False

                self._otherFeathers[room][p] = True
            else:
                if p.startswith('!'): 
                    p = p[1:]
                    self._negate = True

                self._feathers[p] = True

        if len(self._otherFeathers) > 0:
            if len(self._feathers) > 0:
                self._otherFeathers[self._roomName] = self._feathers
                self._negateOther[self._roomName] = self._negate

            i = 0
            for roomName in self._otherFeathers.keys():
                self._enabled[roomName] = False
                from wallaby.pf.room import House
                room = House.get(roomName)

                from functools import partial
                room.catch(Enabler.In.Enable, partial(self._enableOther, roomName))

        else:
            self._catch(Enabler.In.Enable, self._enable)

    # TODO: Was passiert hier? Warum?
    def _enableOther(self, room, pillow, feather):
        if feather in self._otherFeathers[room]:
            self._enabled[room] = not self._negateOther[room]
        else:
            self._enabled[room] = self._negateOther[room]

        enabled = True

        for k, v in self._enabled.items():
            if not v:
                enabled = False

        self._cb(enabled)

        # print "EnableOther", room, pillow, feather, enabled, self._negateOther[room]

    def _enable(self, pillow, feather):
        if feather in self._feathers:
            self._cb(not self._negate)
        else:
            self._cb(self._negate)
