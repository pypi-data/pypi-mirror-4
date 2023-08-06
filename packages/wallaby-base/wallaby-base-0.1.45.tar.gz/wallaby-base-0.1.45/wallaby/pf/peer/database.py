# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

class Database(Peer):
    from wallaby.pf.pillow import Pillow

    #Receiving pillows
    RequestDocument       = Pillow.In
    SaveDocument          = Pillow.In
    CreateAndSaveDocument = Pillow.In
    DeleteDocument        = Pillow.In
    CreateDocument        = Pillow.In

    #Sending pillows
    NewDocument           = Pillow.Out
    RequestedDocument     = Pillow.Out 
    DocumentChanged       = Pillow.Out
    ConnectionRefused     = Pillow.Out 
    ConnectionEstablished = Pillow.Out 
    DocumentNotFound      = Pillow.Out 
    DocumentNotDeleted    = Pillow.Out 
    DocumentNotSaved      = Pillow.Out
    DocumentDeleted       = Pillow.Out
    DocumentCreated       = Pillow.Out
    DocumentSaved         = Pillow.Out

    def __init__(self, *args):
        self._catch(Database.In.RequestDocument, self._getDocument)
        self._catch(Database.In.SaveDocument, self._setDocument)
        self._catch(Database.In.DeleteDocument, self._deleteDocument)
        self._catch(Database.In.CreateDocument, self._createDocument)
        self._catch(Database.In.CreateAndSaveDocument, self._createAndSaveDocument)

    def _getDocument(self, *args):
        pass

    def _setDocument(self, *args):
        pass

    def _deleteDocument(self, *args):
        pass

    def _createDocument(self, *args):
        pass
