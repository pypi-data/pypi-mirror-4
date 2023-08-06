# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

from editDocument import EditDocument
from viewer import Viewer

class Relation(Peer):
    from abstractQuery import AbstractQuery

    Add = Pillow.In
    AddAndSave = Pillow.In

    Sending = [
        EditDocument.In.Rollback, 
        Viewer.In.Document,
        AbstractQuery.In.Query
    ]

    Receiving = [
        Viewer.In.Document,
    ]

    def __init__(self, srcRoom, dstRoom=None, viewIdentifier=None):
        Peer.__init__(self, srcRoom)

        from wallaby.pf.room import House
        self._dstRoom = House.get(dstRoom)

        self._viewIdentifier = viewIdentifier
        self._documentID = None
        self._queryDoc = None
        self._queryRoom = None

        self._catch(Viewer.In.Document, self._docChanged)
        self._catch(Relation.In.Add, self._add)
        self._catch(Relation.In.AddAndSave, self._addAndSave)

        if viewIdentifier != None:
            self._queryRoom = House.get(self._viewIdentifier.upper())

        if self._queryRoom:
            self._queryRoom.catch(Viewer.In.Document, self._queryDocChanged)


    def rooms(self, pillow, feathers):
        rooms = Peer.rooms(self)

        if pillow in (Relation.In.Add, Relation.In.AddAndSave):
            if ';' in feathers:
                dstRoom, relationKey, doc = feathers.split(';')
                if dstRoom == self._dstRoom._name:
                    rooms.add(self._dstRoom._name)

        return rooms

    def destroy(self, remove=False):
        Peer.destroy(self, remove=False)
        if self._queryRoom: self._queryRoom.catch(Viewer.In.Document, self._queryDocChanged)

    def _add(self, pillow, params):
        self._new(params, EditDocument.In.New)

    def _addAndSave(self, pillow, params):
        self._new(params, EditDocument.In.NewAndSave)

    def _new(self, params, sendPillow):
        if self._documentID:
            doc = {}
            dstRoom = self._dstRoom._name
            relationKey = params

            if ';' in params:
                dstRoom, relationKey, doc = params.split(';')
                #print dstRoom, relationKey, doc
                try:
                    import json
                    doc = json.loads(doc)
                except Exception as e:
                    print "JSON ERROR (RELATION)", e
                    doc = {}

            if dstRoom != self._dstRoom._name:
                return

            doc[relationKey] = self._documentID

            print "Try to create new doc", doc, "in room", self._dstRoom
            self._dstRoom.throw(sendPillow, doc, me=self)

    def _queryDocChanged(self, pillow, doc):
        self._queryDoc = doc
        self._refresh(pillow, None)

    def _docChanged(self, pillow, doc):
        if doc == None:
            self._documentID = None
        else:
            self._documentID = doc.documentID

        # self._dstRoom.throw(EditDocument.In.Rollback, None, me=self)
        # self._dstRoom.throw(Viewer.In.Document, None, me=self)
        self._refresh(pillow, None)

    def _refresh(self, pillow, feathers):
        if self._documentID != None and self._queryDoc:
            desc = self._queryDoc.get('args.descending')
            
            if desc:
                self._queryDoc.set('args.endkey', [self._documentID])
                self._queryDoc.set('args.startkey', [self._documentID, {}])
            else:
                self._queryDoc.set('args.startkey', [self._documentID])
                self._queryDoc.set('args.endkey', [self._documentID, {}])


            from multiViewer import MultiViewer
            self._dstRoom.throw(MultiViewer.In.Refresh, None)
