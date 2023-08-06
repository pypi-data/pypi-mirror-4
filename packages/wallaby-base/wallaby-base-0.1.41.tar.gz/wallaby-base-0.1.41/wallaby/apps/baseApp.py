# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

import wallaby.backends.couchdb as couch
from wallaby.pf.peer.credentialsParty import *
from wallaby.pf.peer.configParty import *
from wallaby.pf.peer.credentials import *
from wallaby.pf.room import *
import wallaby.FX as FX

from wallaby.pf.peer.viewer import *
from wallaby.pf.peer.editor import *

class BaseApp(object):
    def __init__(self, quitCB, dbName='default', embedded=False, appName=None, *args, **ka):
        self._dbName = dbName

        self._debuggedRooms = []
        self._debuggers = []
        self._quitCB = quitCB

        self._credentialsInitialized = False

        if not embedded: 
            CredentialsParty(dbName)

            if appName == "inspector":
                ConfigParty("__CONFIG__", dbName, docId="WallabyApp2", inspectorDb=None)
            else:
                ConfigParty("__CONFIG__", dbName, docId="WallabyApp2", inspectorDb="bootstrap")

            House.catch("__CONFIG__", Viewer.In.Refresh, self._configRefreshed)
            House.catch("__CONFIG__", Viewer.In.Document, self._configRefreshed)
            House.catch("__CREDENTIALS__", Credentials.Out.Credential, self._credentialsArrived)

            House.catch("__CONFIG__", Viewer.In.RefreshDone, self._initializeCredentials)

        # House.get("__CONFIG__").initialize()
        # House.get("__CONFIG__").initializePeers()

    def _configRefreshed(self, pillow, feathers):
        if feathers != None:
            House.throw("__CONFIG__:" + Viewer.In.RefreshDone, None)

    def _initializeCredentials(self, pillow, feathers):
        if not self._credentialsInitialized:
            self._credentialsInitialized = True
            House.get("__CREDENTIALS__").initialize()
            House.get("__CREDENTIALS__").initializePeers()

    def quit(self):
        self._quitCB()

    def _credentialsArrived(self, pillow, feathers):
        pass

    def authenticated(self, username=None, password=None, options=None):
        d = defer.Deferred()
        from twisted.internet import reactor
        reactor.callLater(0, self._authenticated, username, password, options, d)
        return d
    
    @defer.inlineCallbacks
    def _authenticated(self, username, password, options, d):
        self.setConnectionSettings(options)

        if username != None:
            couch.Database.setLoginForDatabase(self.dbName(), username, password)

        authorized = False
        try:
            authorized = yield couch.Database.testConnectionToDatabase(self.dbName())
        except Exception as e:
            print "Exception while login", e 

        if authorized:
            options.username = username
            options.password = password
            self.setConnectionSettings(options) # reset connection settings

            from twisted.internet import reactor
            reactor.callLater(0, couch.Database.getDatabase(self.dbName()).changes)
            d.callback(True)
        else:
            d.callback(False)

    def run(self, checkRoom=None):
        dbname = self.dbName()
        if dbname == None:
            return

        for debugger in self._debuggers:
            debugger.destroy()

        # House.get("__CONFIG__").initialize()
        # House.get("__CONFIG__").initializePeers()
        House.get("__CONFIG__").configUpdated(None, force=True)

        for room in self._debuggedRooms:
            from wallaby.pf.peer.debugger import Debugger
            self._debuggers.append(Debugger(room, "*"))

        if checkRoom != None:
            House.get(checkRoom).check(suggest=True)

        self.isRunning()

    def isRunning(self):
        pass

    def setConnectionSettings(self, options):
        pass

    def dbName(self):
        return self._dbName
