# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

class SdEdit(Peer):
    def __init__(self, room, host='localhost', port=60001, actors = None):
        Peer.__init__(self, room)

        self._roomName = room

        self._catch('*', self._message, passCaller=True)

        if actors == None: actors = {}

        self._host = host
        self._port = port

        self._actors = actors

        from wallaby.pf.log.sdeditChannelFactory import SDEditChannelFactory
        self._factory = SDEditChannelFactory()

        self._initialized = False

    def initialize(self):
        if self._initialized: return
        self._initialized = True

        pillows = House.rooms[self._roomName].registeredPillows

        self._peers = {}
        self._pillows = {}
        self._translation = {}
        for key, callbacks in pillows.items():
            for (callback, thrower) in callbacks:
                className = callback.im_self.__class__.__name__
                if len(self._actors) == 0 or className in self._actors:
                    if className in self._actors:
                        trans = self._actors[className]

                        if isinstance(trans, str) or isinstance(trans, unicode):
                            self._translation[className] = trans
                            className = trans
                        else:
                            if not trans:
                                pass 

                    if not className in self._peers: self._peers[className] = {}
                    if not key in self._pillows: self._pillows[key] = {}

                    self._peers[className][key] = True
                    self._pillows[key][className] = True

        for peer in self._actors:
            if peer in self._translation:
                peer = self._translation[peer]

            if peer in self._actors:
                trans = self._actors[peer]

                if isinstance(trans, str) or isinstance(trans, unicode):
                    self._translation[peer] = trans
                    peer = trans

            if peer not in self._peers:
                self._peers[peer] = {}


        self._factory.configure(peers=self._peers, room=self._roomName, pillows=self._pillows, translations=self._translation)

        from twisted.internet import reactor
        reactor.connectTCP(self._host, self._port, self._factory)

    def _message(self, pillow, feathers, caller=None):
        self._factory.sendMessage(caller.__class__.__name__, pillows, feathers)
