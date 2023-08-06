# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

class DocumentCredentials(Peer):
    # Message to request the credential document from backend
    RequestDocument = Pillow.Out
    SaveDocument = Pillow.Out

    # The requested credential document
    RequestedDocument = Pillow.In
    DocumentNotFound = Pillow.In
    DocumentCreated = Pillow.In

    Singleton = None

    def __init__(self, room, documentID="credentials"):
        Peer.__init__(self, room)
        self._documentID = documentID
        self._catch(DocumentCredentials.In.RequestedDocument, self._requestedDocument)
        self._catch(DocumentCredentials.In.DocumentNotFound, self._docNotFound)
        self._catch(DocumentCredentials.In.DocumentCreated, self._docCreated)

        DocumentCredentials.Singleton = self

        self._initialized = False

    @staticmethod
    def request():
        if DocumentCredentials.Singleton == None: return
        DocumentCredentials.Singleton.reinitialize()

    def _docCreated(self, pillow, id):
        if id != self._documentID: return
        self._update()

        # self._throw(DocumentCredentials.Out.RequestDocument, self._documentID)

    def _docNotFound(self, pillow, id):
        if id != self._documentID: return
        from wallaby.common.document import Document
        self._credentials = Document(self._documentID)
        self._throw(DocumentCredentials.Out.SaveDocument, (self._credentials, None))

        self._requestedDocument(None, self._credentials)

    def reinitialize(self):
        self._initialized = False
        self.initialize()

    def initialize(self):
        if self._initialized: return
        self._initialized = True

        self._throw(DocumentCredentials.Out.RequestDocument, self._documentID)

    def _requestedDocument(self, pillow, document):
        if document.documentID == self._documentID:
            self._credentials = document
            self._update()

    def _update(self, *args):
        from credentials import Credentials
        self._throw(Credentials.Out.Credential, self._credentials)
