# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

from wallaby.common.document import Document

class RoomDebugger(Peer):

    RequestRooms  = Pillow.In
    RequestDebugInfo = Pillow.In

    RequestedRooms  = Pillow.Out
    RequestedDebugInfo = Pillow.Out

    def __init__(self, room):
        Peer.__init__(self, room)
        self._roomName = room
        self._catch(ContextDebugger.In.RequestRooms, self._rooms)
        self._catch(ContextDebugger.In.RequestDebugInfo, self._info)

    def _rooms(self, pillow, feathers):
        dict = {'_id':'rooms'}
        rooms = House.rooms.keys()
        rooms.sort()

        dict['titles'] = rooms
        document = Document(data=dict)
        self._throw(ContextDebugger.Out.RequestedRooms, document)

    def _info(self, pillow, feathers):
        # Get registered pillows and feathers
        pillows = None
        dict = {'_id':'pillows','room':feathers}

        if feathers in House.rooms:
            pillows = House.rooms[feathers].registeredPillows
            inBoundPillows = House.rooms[feathers].inBoundPillows()
            outBoundPillows = House.rooms[feathers].outBoundPillows()
            peers = House.rooms[feathers].peers()
        else:
            pillows = House.rooms[self._roomName].registeredPillows
            inBoundPillows = House.rooms[self._roomName].inBoundPillows()
            outBoundPillows = House.rooms[self._roomName].outBoundPillows()
            peers = House.rooms[self._roomName].peers()
            dict['room'] = self._roomName

        pillowKeys = pillows.keys()
        pillowKeys.sort()

        pillowDicts = []

        for pillow in pillowKeys:
            callbackDict = {}
            callbacks = pillows[pillow]
            for callback,_ in callbacks:
                className = callback.im_self.__class__.__name__
                functionName = callback.im_func.__name__
                if className in callbackDict and callbackDict[className]['function'] == functionName:
                    callbackDict[className]['count'] += 1
                else:
                    callbackDict[className] = {'class':callback.im_self.__class__.__name__,'function':callback.im_func.__name__,'count':1}

            keys = callbackDict.keys()
            keys.sort()
            callbackDicts = []
            for key in keys:
                callbackDicts.append(callbackDict[key])

            pillowDicts.append({'name':pillow,'callbacks':callbackDicts})

        dict['pillows'] = pillowDicts

        # Get unhandled and uncalled pillows
        observer = House.observer()

        # Uncalled pillows
        uncalled = []
        for fqa in inBoundPillows:
            if fqa not in outBoundPillows:
                peers = observer.outBoundPeers(fqa, True)
                
                runtimeObject = False

                for p in peers:
                    if observer.objectType(p) == Pillow.Runtime:
                        runtimeObject = True

                if runtimeObject:
                    continue

                uc = {'pillow': fqa, 'suggests': []}

                try:
                    plw = fqa.split('.')[2]
                    lst = observer.outBoundPeers(plw)
                    if lst: uc['suggests'] =  lst
                except:
                    print "ERROR - split:", plw

                uncalled.append(uc)

        dict['uncalled'] = uncalled

        # Unhandled pillows
        unhandled = []
        for fqa in outBoundPillows:
            if fqa not in inBoundPillows:
                peers = observer.inBoundPeers(fqa, True)
                
                runtimeObject = False

                for p in peers:
                    if magic.objectType(p) == Pillow.Runtime:
                        runtimeObject = True

                if runtimeObject:
                    continue

                uh = {'pillow': fqa, 'suggests': []}

                try:
                    plw = fqa.split('.')[2]
                    lst = observer.inBoundPeers(act)
                    if lst: uh['suggests'] = lst
                except:
                    print "ERROR - split:", act

                uncalled.append(uc)

        dict['unhandled'] = unhandled

        unregistered = []
        for fqa in inBoundPillows:
            if fqa not in peers:
                unregistered.append({'pillow': fqa})    

        dict['unregistered'] = unregistered

        document = Document(data=dict)
        self._throw(ContextDebugger.Out.RequestedDebugInfo, document)
