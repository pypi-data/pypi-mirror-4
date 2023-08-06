# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

from abstractQuery import AbstractQuery
from documentCache import DocumentCache
from editDocument import EditDocument
from multiViewer import MultiViewer
from tab import Tab

class MultiViewQuery(Peer):
    Description = ("Routing between a multi-view element (like a table) and a query-peer (like a database)",
                   '{ "dstRoom": null, "pillow": "EditDocument.In.Load", "unload": true }')

    Sending = [
        EditDocument.In.Load, 
        Tab.In.Select,
    ]

    Receiving = [
        MultiViewer.Out.Select
    ]

    Routings = [
        (AbstractQuery.Out.Result, MultiViewer.In.Data),
        (DocumentCache.Out.DocumentChanged, MultiViewer.In.DataChanged),
        (MultiViewer.Out.Query, AbstractQuery.In.Query)
    ]

    def __init__(self, room, dstRoom=None, pillow=EditDocument.In.Load, unload=True):
        Peer.__init__(self, room)
        self._pillow = pillow

        if dstRoom is None: dstRoom = room
        self._dstRoom = dstRoom
        self._unload = unload

        self._catch(MultiViewer.Out.Select, self._select)

    def rooms(self, pillow, feathers):
        rooms = Peer.rooms(self)
        if pillow == MultiViewer.Out.Select:
            rooms.add(self._dstRoom)

        return rooms

    def _select(self, pillow, feathers):
        id, tab, idx  = feathers

        if not self._unload and id == None:
            return

        if self._pillow != None:
            if isinstance(self._pillow, (list, tuple)):
                for p in self._pillow:
                    self._throw(self._dstRoom + ":" + p, id)
            else:
                self._throw(self._dstRoom + ":" + self._pillow, id)
        if tab != None:
            self._throw(self._dstRoom + ":" + Tab.In.Select, tab)
