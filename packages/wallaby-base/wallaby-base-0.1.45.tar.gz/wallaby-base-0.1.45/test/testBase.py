# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from twisted.internet import defer, reactor
from twisted.trial import unittest

from wallaby.pf.room import House
from wallaby.pf.peer.peer import Peer
from wallaby.pf.peer.credentialsParty import CredentialsParty

factory = House.observer()

def sleep(time):
    d = defer.Deferred()
    reactor.callLater(time, d.callback, None)
    return d

class WallabyCouchDBTest(unittest.TestCase):
    def setUp(self):
        self._dbName = "wallaby_test"
        self._docId  = "testdoc"
        self.timeout = 1

        self._designDoc = {
           "_id": "_design/wallaby_test",
           "language": "javascript",
           "views": {
               "text": {
                   "map": "function(doc) { if(doc.text)\n   emit(doc.text, null);\n}"
               }
           },
           "filters": {
               "typeB": "function(doc, req) { if((doc.type && doc.type == \"typeB\") || doc.deleted) { return true; } return false;}"
           }
        }

        import wallaby.backends.couchdb as couch
        self._db = couch.Database.getDatabase(self._dbName)

    def tearDown(self):
        import wallaby.backends.couchdb as couch
        couch.Database.closeDatabase(self._dbName)

    @defer.inlineCallbacks
    def getDoc(self, name):
        doc = yield self._db.get(name)
        self.assertTrue(doc != None)
        self.assertEqual(doc["_id"], name)
        defer.returnValue(doc)

    @defer.inlineCallbacks
    def test_00_initialize(self):
        try:
            info = yield self._db.info(keepOnTrying=False, returnOnError=True)
            if info != None: 
                yield self._db.destroy()
        except:
            pass

        ret = yield self._db.create()
        self.assertTrue(ret["ok"])
        yield self._db.save(self._designDoc)
        yield self._db.save({"_id": self._docId, "text":"Hello World!"})
        yield self._db.save({"_id": "credentials"})

    @defer.inlineCallbacks
    def test_01_database(self):
        global factory
        peers = ["CouchDB"]

        for p in peers:
            factory.peer(p, "room01")

        House.initializeAll()
        Peer.initializeAll()
        yield sleep(0.1)

        d = defer.Deferred()

        room = House.get("room01")

        from wallaby.pf.peer.database import Database
        room.catch(Database.Out.RequestedDocument, lambda *args: d.callback(args))
        room.throw(Database.In.RequestDocument, self._docId)

        pillow, doc = yield d
        self.assertEqual(doc.documentID, self._docId)

        House.destroyRoom("room01")

    @defer.inlineCallbacks
    def test_02_view(self):
        global factory
        peers = ["ViewDocument", "DocumentCache", "DocumentDatabase", "CouchDB"]

        for p in peers:
            factory.peer(p, "room01")

        CredentialsParty()

        d = defer.Deferred()
        def callback(value):
            if value:
                d.callback(value)

        from wallaby.pf.peer.viewer import Viewer
        Viewer("room01", callback, "text")

        House.initializeAll()
        Peer.initializeAll()
        yield sleep(0.1)

        from wallaby.pf.peer.editDocument import EditDocument
        room = House.get("room01")
        room.throw(EditDocument.In.Load, self._docId)

        value = yield d
        self.assertEqual(value, "Hello World!")

        House.destroyRoom("room01")
        House.destroyRoom("__CREDENTIALS__")

    @defer.inlineCallbacks
    def test_03_edit(self):
        global factory
        peers = ["EditDocument", "DocumentCache", "DocumentDatabase", "CouchDB"]

        for p in peers:
            factory.peer(p, "room01")

        CredentialsParty()

        valueDeferred = defer.Deferred()
        def valueCallback(value):
            if value == "Hello Jan": 
                try:
                    valueDeferred.callback(value)
                except: pass

        setRODeferred = defer.Deferred()
        def roCallback(readOnly):
            if not readOnly: 
                try:
                    setRODeferred.callback(readOnly)
                except: pass

        from wallaby.pf.peer.viewer import Viewer
        from wallaby.pf.peer.editor import Editor
        Viewer("room01", valueCallback, "text")
        editor = Editor("room01", path="text", setReadOnlyCallback=roCallback)

        House.initializeAll()
        Peer.initializeAll()
        yield sleep(0.1)

        from wallaby.pf.peer.editDocument import EditDocument
        room = House.get("room01")
        room.throw(EditDocument.In.LoadAndEdit, self._docId)
        
        yield setRODeferred
        editor.changeValue("Hello Jan")

        value = yield valueDeferred
        self.assertEqual(value, "Hello Jan")

        room.throw(EditDocument.In.Save, self._docId)

        from wallaby.pf.peer.database import Database
        docId = yield room.catchNow(Database.Out.DocumentSaved)
        self.assertEqual(docId, self._docId)

        doc = yield self._db.get(self._docId)
        self.assertEqual(doc["text"], "Hello Jan")

        House.destroyRoom("room01")
        House.destroyRoom("__CREDENTIALS__")

    @defer.inlineCallbacks
    def test_99_destroy(self):
        res = yield self._db.destroy()
        self.assertTrue(res["ok"])
