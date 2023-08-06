# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

import os, string, re
import wallaby.FX as FX

class Observer(object):
    def __init__(self):
        self._inBoundPillows = {}
        self._inBoundPillowsFQ = {}
        self._outBoundPillows = {}
        self._outBoundPillowsFQ = {}
        self._inBoundPillowsPerPeer = {}
        self._outBoundPillowsPerPeer = {}
        self._objectTypes = {}
        self._extendedBy = {}
        self._bases = {}
        self._peers = {}
        self._rooms = {}
        self._fqn = {}

    def peerClass(self, name):
        if name in self._peers:
            return self._peers[name]
        else:
            return None

    def peer(self, name, *args, **ka):
        if name in self._peers:
            return self._peers[name](*args, **ka)
        else:
            return None

    def allPeers(self):
        return self._peers

    def allInBoundPillows(self):
        return self._inBoundPillowsFQ

    def allOutBoundPillows(self):
        return self._outBoundPillowsFQ

    def peers(self, pillow, lst):
        if not pillow in lst:
            return []
        else:
            peers = lst[pillow]
            allPeers = {}
            self._appendPeers(peers, allPeers)
            return allPeers.keys()

    def objectType(self, peer):
        if not peer in self._objectTypes:
            return None
        else:
            return self._objectTypes[peer]

    def _appendPeers(self, _from, _to):
        for peer in _from:
            _to[peer] = True 
            if peer in self._extendedBy:
                self._appendPeers(self._extendedBy[peer], _to)

    def pillows(self, peer, lst):
        if peer in lst:
            pillows = lst[peer]
        else:
            pillows = []

        allPillows = {}
        self._appendPillows(peer, lst, pillows, allPillows)
        return allPillows.keys()

    def _appendPillows(self, peer, lst, _from, _to):
        for pillow in _from:
            _to[pillow] = True 

        if peer in self._bases:
            for h in self._bases[peer]:
                if h in lst:
                    pillows = lst[h]
                else:
                    pillows = []

                self._appendPillows(h, lst, pillows, _to)

    def outBoundPillows(self, peer=None):
        if peer==None:
            return self._outBoundPillows.keys()
        else:
            if '.' not in peer and peer in self._fqn: 
                peer = self._fqn[peer]
               
            return self.pillows(peer, self._outBoundPillowsPerPeer)

    def inBoundPillows(self, peer=None):
        if peer==None:
            return self._inBoundPillows.keys()
        else:
            if '.' not in peer and peer in self._fqn: 
                peer = self._fqn[peer]

            return self.pillows(peer, self._inBoundPillowsPerPeer)

    def outBoundPeers(self, pillow=None, fq=False):
        if pillow==None:
            return self._outBoundPillowsPerPeer.keys()
        else:
            pillow = pillow.replace('!', '')
            if fq:
                return self.peers(pillow, self._outBoundPillowsFQ)
            else:
                return self.peers(pillow, self._outBoundPillows)

    def inBoundPeers(self, pillow=None, fq=False):
        if pillow==None:
            return self._inBoundPillowsPerPeer.keys()
        else:
            pillow = pillow.replace('!', '')
            if fq:
                return self.peers(pillow, self._inBoundPillowsFQ)
            else:
                return self.peers(pillow, self._inBoundPillows)

    def scan(self, peers=None):
        fqPeers = []

        if peers is None:
            import wallaby.pf.peer as peers
            from twisted.plugin import getCache
            peers = getCache(peers)
            root = "wallaby.pf.peer"

            for peer in peers:
                fqPeers.append(root + "." + peer)
        else:
            fqPeers = peers

        for fqPeer in fqPeers:
            
            mod = FX.imp(fqPeer)
            root, basename = fqPeer.rsplit('.', 1)

            if mod == None: continue

            cls = string.upper(basename[0]) + basename[1:]                       

            if not cls in mod.__dict__: continue

            fqn = root + '.' + basename + '.' + cls

            self._fqn[cls] = fqn

            if re.search(r"\.room", root) != None:
                self._rooms[cls] = mod.__dict__[cls]
            else:
                self._peers[cls] = mod.__dict__[cls]

            self._objectTypes[fqn] = mod.__dict__[cls].ObjectType

            for base in mod.__dict__[cls].__bases__:
                fqBase = base.__module__ + '.' + base.__name__
                if not fqBase in self._extendedBy:
                    self._extendedBy[fqBase] = set()

                self._extendedBy[fqBase].add(fqn)

                if not fqn in self._bases:
                    self._bases[fqn] = set()

                self._bases[fqn].add(fqBase)

            if 'Receiving' in mod.__dict__[cls].__dict__:
                for fqa in mod.__dict__[cls].Receiving:
                    pillow = None
                    try:
                        pillow = fqa.split('.')[2]
                    except:
                        print "Split error:", fqa

                    pillow = pillow.replace('!', '')
                    fqa = fqa.replace('!', '')

                    if not pillow in self._inBoundPillows: self._inBoundPillows[pillow] = []
                    if not fqa in self._inBoundPillowsFQ: self._inBoundPillowsFQ[fqa] = []
                    if not fqn in self._inBoundPillowsPerPeer: self._inBoundPillowsPerPeer[fqn] = []
                    self._inBoundPillows[pillow].append(fqn)
                    self._inBoundPillowsFQ[fqa].append(fqn)
                    self._inBoundPillowsPerPeer[fqn].append(fqa)


            for pillow in mod.__dict__[cls].InPillows:
                pillow = pillow.replace('!', '')

                fqa = cls + '.In.' + pillow
                fqa = fqa.replace('!', '')

                if not pillow in self._inBoundPillows: self._inBoundPillows[pillow] = []
                if not fqa in self._inBoundPillowsFQ: self._inBoundPillowsFQ[fqa] = []
                if not fqn in self._inBoundPillowsPerPeer: self._inBoundPillowsPerPeer[fqn] = []
                self._inBoundPillows[pillow].append(fqn)
                self._inBoundPillowsFQ[fqa].append(fqn)
                self._inBoundPillowsPerPeer[fqn].append(fqa)

            if 'Sending' in mod.__dict__[cls].__dict__:
                for fqa in mod.__dict__[cls].Sending:
                    pillow = None
                    try:
                        pillow = fqa.split('.')[2]
                    except:
                        print "Split error:", fqa

                    fqa = fqa.replace('!', '')
                    pillow = pillow.replace('!', '')

                    if not pillow in self._outBoundPillows: self._outBoundPillows[pillow] = []
                    if not fqa in self._outBoundPillowsFQ: self._outBoundPillowsFQ[fqa] = []
                    if not fqn in self._outBoundPillowsPerPeer: self._outBoundPillowsPerPeer[fqn] = []
                    self._outBoundPillows[pillow].append(fqn)
                    self._outBoundPillowsFQ[fqa].append(fqn)
                    self._outBoundPillowsPerPeer[fqn].append(fqa)

            for pillow in mod.__dict__[cls].OutPillows:
                pillow = pillow.replace('!', '')

                fqa = cls + '.Out.' + pillow
                fqa = fqa.replace('!', '')
                if not pillow in self._outBoundPillows: self._outBoundPillows[pillow] = []
                if not fqa in self._outBoundPillowsFQ: self._outBoundPillowsFQ[fqa] = []
                if not fqn in self._outBoundPillowsPerPeer: self._outBoundPillowsPerPeer[fqn] = []
                self._outBoundPillows[pillow].append(fqn)
                self._outBoundPillowsFQ[fqa].append(fqn)
                self._outBoundPillowsPerPeer[fqn].append(fqa)


