# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

# Common imports 
from wallaby.pf.pillow import Pillow
from twisted.internet import defer

class Peer(object):
    from wallaby.pf.pillow import Pillow

    __metaclass__ = Pillow

    peers = []

    def __init__(self, roomName):
        if roomName == None: roomName = "None"

        self.initialized = False

        from wallaby.pf.room import House
        self.__room = House.get(roomName)
        Peer.peers.append(self)

        self._roomName = roomName

        self._routings = {}
        self._peers = []
        self._catchers = set()

        if 'Routings' in self.__class__.__dict__:
            for f, t in self.__class__.Routings:
                self._addRouting(f, t)

        self.destroyed = False
        self.__room.enter(self)

        from wallaby.pf.peer.viewer import Viewer

    def rooms(self, *args):
        from wallaby.common.sets import OrderedSet
        rooms = OrderedSet()
        rooms.add(self._roomName)
        return rooms

    def dynamicPillows(self):
        return []

    @classmethod
    def initializeAll(cls, onlyNew=False):
        for peer in Peer.peers:
            if not peer.initialized or not onlyNew:
                peer.initialize()
                peer.initialized = True

    def destroy(self, remove=False):
        s = set(self._catchers)
        for act in s: self._uncatch(*act)
        for p in self._peers: p.destroy()
        if remove and self in Peer.peers: Peer.peers.remove(self)

        self._catchers = set()

        self.__room.leave(self)
        self.destroyed = True

    def add(self, peer):
        self._peers.append(peer)

    def _addRouting(self, sourcePillow, destinationPillow):
        if not sourcePillow in self._routings:
            self._routings[sourcePillow] = set()
            self._catch(sourcePillow, self._routePillow)

        self._routings[sourcePillow].add(destinationPillow)

    def _routePillow(self, pillow, feathers):
        if pillow in self._routings:
            for routing in self._routings[pillow]:
                self.__room.throw(routing, feathers, caller=self)

    def initialize(self):
        pass

    def _throw(self, pillow, feather, me=None):
        if not me: me = self
        tokens = str(pillow).split('.')
        if len(tokens) > 1 and tokens[1] == "Out":
            self.__room.throw(pillow, feather, me=me)
        else:
            self.__room.throw(pillow, feather, me=me)

    def _uncatch(self, pillow, catcher, passThrower=False):
        ident = pillow, catcher, passThrower

        self.__room.uncatch(*ident)

        try:
            self._catchers.remove(ident)
        except:
            pass

    def _catch(self, pillow, catcher, passThrower=False):
        ident = pillow, catcher, passThrower

        tokens = str(pillow).split('.')
        if pillow == '*' or len(tokens) > 1 and tokens[1] == "In":
            self.__room.catch(*ident)
        else:
            #print "Deprecated catcher", pillow, "in", self.__class__.__name__
            #TODO: REFACTOR PEERS
            self.__room.catch(*ident)

        self._catchers.add(ident)
