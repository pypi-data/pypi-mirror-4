# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from twisted.internet.protocol import ClientFactory, Protocol
from datetime import *
from twisted.internet import defer
import re

class SDEditChannelProtocol(Protocol):
    def __init__(self):
        self._data = ""
        self._peers = {}
        self._thread = {}
        self._queue = []
        self._room = "UNKNOWN"
        self._connected = False

    def configure(self, peers=None, room=None, pillows=None, translations=None):
        self._peers = peers
        self._room = room
        self._pillows = pillows
        self._translations = translations

    def sendMessage(self, *args):
        if not self._connected:
            self._queue.append(args)
        else:
            self.doSendMessage(*args)

    def doSendMessage(self, sender, pillow, feathers):
        if pillow in self._pillows:
            if (isinstance(feathers, unicode) or isinstance(feathers, str)) and len(feathers) == 32:
                feathers = "..." + feathers[27:31]

            feathers = str(feathers)
            feathers = feathers.replace(':', '=')
            pillowStr = pillow + '(' + feathers + ')'

            if sender in self._translations:
                sender = self._translations[sender]

            if sender not in self._peers: return

            receivers = self._pillows[pillow].keys() 
            if len(receivers) > 1:
                self.transport.write(sender + ':>{' + (','.join(receivers)) + '}.' + pillowStr + '\n')
            elif len(receivers) == 1:
                self.transport.write(sender + ':>' + receivers[0] + '.' + pillowStr + '\n')

            for r in receivers:
                self.transport.write(r + ':stop\n')

    def connectionMade(self):
        self._connected = True
        self.transport.write(self._room+'\n')
        self.transport.write('Room:Actor\n')

        for h in self._peers.keys():
            self.transport.write(h+':'+h+'[a]\n')

        self.transport.write('\n')
        self.transport.write('room:{'+(','.join(self._peers.keys()))+'}.initialize\n')

        while len(self._queue) > 0:
            args = self._queue.pop()
            self.doSendMessage(*args)

    def connectionLost(self, reason):
        pass

    def dataReceived(self, data):
        pass

class SDEditChannelFactory(ClientFactory):
    protocol = SDEditChannelProtocol

    def __init__(self):
        self._config = None
        self._connectedProtocol = None
        self._queue = []

    def configure(self, **args):
        self._config = args

    def sendMessage(self, *args):
        if self._connectedProtocol != None:
            self._connectedProtocol.sendMessage(*args)
        else:
            self._queue.append(args)

    def buildProtocol(self, address):
        self._connectedProtocol = ClientFactory.buildProtocol(self, address)

        if self._config != None: 
            self._connectedProtocol.configure(**self._config)

        while len(self._queue) > 0:
            args = self._queue.pop()
            self._connectedProtocol.sendMessage(*args)

        return self._connectedProtocol
