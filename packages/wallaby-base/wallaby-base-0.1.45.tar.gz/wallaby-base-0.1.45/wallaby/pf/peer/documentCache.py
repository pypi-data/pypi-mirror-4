# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

from wallaby.common.document import Document
from documentChanger import DocumentChanger

class DocumentCache(Peer):
    from wallaby.pf.pillow import Pillow

    Description = "Provides caching and shadow copy mechanism for documents"

    Suggests = [
        "DocumentDatabase"
    ]

    #Receiving Pillows
    ForgetDocument = Pillow.In
    DeleteShadowCopy = Pillow.In
    CreateShadowCopy = Pillow.In
    ReplaceShadowCopy = Pillow.In
    ChangesInShadowCopy = Pillow.In
    StoreShadowCopy = Pillow.In
    StoreShadowCopyAs = Pillow.In

    RequestDocument = Pillow.InOut
    DocumentChanged = Pillow.InOut
    DeleteDocument = Pillow.InOut
    DocumentSaved = Pillow.InOut
    CreateDocument = Pillow.InOut
    CreateAndSaveDocument = Pillow.InOut
    DocumentCreated = Pillow.InOut
    RequestedDocument = Pillow.InOut

    #Sending Pillows
    SaveDocument = Pillow.Out
    ShadowCopyAlreadyExists = Pillow.Out
    DoesNotExist = Pillow.Out
    ShadowCopyNotFound = Pillow.Out

    def __init__(self, *args):
        Peer.__init__(self, *args)
        self._documentStore = {} # id -> document
        self._shadowCopyStore = {} # id -> document
        self._requestedDocuments = [] # id

        self._catch(DocumentCache.In.DocumentChanged, self._documentChanged)
        self._catch(DocumentCache.In.CreateDocument, self._createDocument)
        self._catch(DocumentCache.In.CreateAndSaveDocument, self._createAndSaveDocument)
        self._catch(DocumentCache.In.DocumentCreated, self._documentCreated)
        self._catch(DocumentCache.In.RequestedDocument, self._documentFromDatabase)
        self._catch(DocumentCache.In.RequestDocument, self._requestDocument)
        self._catch(DocumentCache.In.ForgetDocument, self._forgetDocument)
        self._catch(DocumentCache.In.DeleteDocument, self._deleteDocument)
        self._catch(DocumentCache.In.DeleteShadowCopy, self._deleteShadowCopy)
        self._catch(DocumentCache.In.CreateShadowCopy, self._createShadowCopy)
        self._catch(DocumentCache.In.ChangesInShadowCopy, self._changesInShadowCopy)
        self._catch(DocumentCache.In.ReplaceShadowCopy, self._replaceShadowCopy)
        self._catch(DocumentCache.In.StoreShadowCopy, self._storeShadowCopy)
        self._catch(DocumentCache.In.StoreShadowCopyAs, self._storeShadowCopyAs)
        self._catch(DocumentCache.In.DocumentSaved, self._documentSaved)

    def _documentChanged(self, pillow, (documentID, rev) ):
        if documentID in self._documentStore:
            if rev == self._documentStore[documentID].rev():
                # ignore already known revision
                return

            self._throw(DocumentCache.Out.RequestDocument, documentID)

    def _documentCreated(self, pillow, doc):
        self._shadowCopyStore[doc.documentID] = doc
        self._throw(DocumentCache.Out.DocumentCreated, doc)

    @defer.inlineCallbacks
    def _createDocument(self, pillow, doc):
        if isinstance(doc, str) or isinstance(doc, unicode):
            try:
                doc = yield DocumentChanger.transform(None, doc)
            except Exception as e:
                doc = None
                print "ERROR - Exception: " + str(e)

        if type(doc) is dict:
            self._throw(DocumentCache.Out.CreateDocument, doc)
        else:
            self._throw(DocumentCache.Out.CreateDocument, None)

    @defer.inlineCallbacks
    def _createAndSaveDocument(self, pillow, doc):
        if isinstance(doc, str) or isinstance(doc, unicode):
            try:
                doc = yield DocumentChanger.transform(None, doc)
            except Exception as e:
                doc = None
                print "ERROR - Exception: " + str(e)

        if type(doc) is dict:
            self._throw(DocumentCache.Out.CreateAndSaveDocument, doc)
        else:
            self._throw(DocumentCache.Out.CreateAndSaveDocument, None)

    def _documentFromDatabase(self, pillow, document):
        if document == None: return
            
        if document.documentID in self._documentStore:
            if document.rev() == self._documentStore[document.documentID].rev(): 
                # Ignore same revision
                return

            document.selection = self._documentStore[document.documentID].selection
            self._documentStore[document.documentID]=document
            self._throw(DocumentCache.Out.DocumentChanged, document)
        elif document.documentID in self._requestedDocuments:
            self._documentStore[document.documentID]=document
            self._requestedDocuments.remove(document.documentID)
            self._requestDocument(None, document.documentID)

    def _requestDocument(self, pillow, documentID):
        if documentID in self._documentStore:
            self._throw(DocumentCache.Out.RequestedDocument, self._documentStore[documentID])
        elif documentID in self._shadowCopyStore:
            self._throw(DocumentCache.Out.RequestedDocument, self._shadowCopyStore[documentID])
        elif documentID not in self._requestedDocuments:
            self._requestedDocuments.append(documentID)
            self._throw(DocumentCache.Out.RequestDocument, documentID)

    def _forgetDocument(self, pillow, documentID):
        if documentID in self._documentStore:
            del self._documentStore[documentID]
        if documentID in self._shadowCopyStore:
            del self._shadowCopyStore[documentID]
        if documentID in self._requestedDocuments:
            self._requestedDocuments.remove(documentID)

    def _deleteDocument(self, pillow, documentID):
        if documentID in self._documentStore:
            document = self._documentStore[documentID]
            self._forgetDocument(pillow, documentID)
            self._throw(DocumentCache.Out.DeleteDocument, document)
        else:
            self._throw(DocumentCache.Out.DoesNotExist, documentID)

    def _deleteShadowCopy(self, pillow, documentID):
        if documentID not in self._shadowCopyStore:
            self._throw(DocumentCache.Out.ShadowCopyNotFound, documentID)
        else:
            del self._shadowCopyStore[documentID]

    def _replaceShadowCopy(self, pillow, documentID):
        self._deleteShadowCopy(pillow, documentID)
        self._createShadowCopy(pillow, documentID)

    def _createShadowCopy(self, pillow, documentID):
        if documentID not in self._documentStore:
            self._throw(DocumentCache.Out.DoesNotExist, documentID)
        elif documentID in self._shadowCopyStore:
            self._throw(DocumentCache.Out.ShadowCopyAlreadyExists, documentID)
        else:
            doc = self._documentStore[documentID]

            import copy
            self._documentStore[documentID] = copy.deepcopy(doc)
            self._shadowCopyStore[documentID] = doc

    def _changesInShadowCopy(self, pillow, documentID):
        if documentID not in self._documentStore:
            self._throw(DocumentCache.Out.DoesNotExist, documentID)
        else:
            self._documentStore[documentID].changes(self._shadowCopyStore[documentID])
            pass

    def _storeShadowCopyAs(self, pillow, (documentID, newID)):
        if documentID not in self._shadowCopyStore and documentID in self._documentStore:
            self._shadowCopyStore[documentID] = self._documentStore[documentID]  

        if documentID not in self._shadowCopyStore:
            self._throw(DocumentCache.Out.ShadowCopyNotFound, documentID)
        else:
            shadowCopy  = self._shadowCopyStore[documentID]

            shadowCopy = shadowCopy.clone()
            shadowCopy.resetDocumentID(newID)
            documentID = newID

            self._shadowCopyStore[documentID] = shadowCopy

            self._throw(DocumentCache.Out.SaveDocument, (shadowCopy, None) )

    def _storeShadowCopy(self, pillow, documentID):
        if documentID not in self._shadowCopyStore:
            self._throw(DocumentCache.Out.ShadowCopyNotFound, documentID)
        else:
            shadowCopy  = self._shadowCopyStore[documentID]
            oldDocument = None

            if documentID in self._documentStore:
                oldDocument = self._documentStore[documentID]
                shadowCopy.solveConflicts(oldDocument)

            # Update changed document in document store.
            # Needed for Databases without changes stream! 
            self._documentStore[documentID] = shadowCopy

            self._throw(DocumentCache.Out.SaveDocument, (shadowCopy, oldDocument) )

    def _documentSaved(self, pillow, documentID):
        if documentID in self._shadowCopyStore:
            self._deleteShadowCopy(None, documentID)

        self._throw(DocumentCache.Out.DocumentSaved, documentID)

