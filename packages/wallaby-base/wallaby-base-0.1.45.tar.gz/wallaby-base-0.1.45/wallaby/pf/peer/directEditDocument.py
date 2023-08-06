# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

from documentCache import DocumentCache
from documentChanger import DocumentChanger
from database import Database
from viewer import Viewer
from editor import Editor

class DirectEditDocument(Peer):
    Description = ("Provides a direct document edit/view logic", '{"id": null}')

    Save = Pillow.In
    SaveAs = Pillow.In
    Load = Pillow.In

    ChangeID = Pillow.In

    Sending = [
        Viewer.In.Document,
        Viewer.In.Refresh,
        Editor.In.Enable,
        DocumentCache.In.CreateShadowCopy,
        DocumentCache.In.RequestDocument
    ]

    Receiving = [
        DocumentCache.Out.RequestedDocument,
        DocumentCache.Out.DocumentChanged,
        DocumentCache.Out.DocumentSaved
    ]

    Routings = [
        (Editor.Out.FieldChanged, Viewer.In.Refresh)
    ]

    def __init__(self, room, id=None):
        Peer.__init__(self, room)

        self._id = id
        self._newID = id
        self._doc = None
        self._requestNew = False

        self._catch(DirectEditDocument.In.Load, self._load)
        self._catch(DirectEditDocument.In.Save, self._save)
        self._catch(DirectEditDocument.In.SaveAs, self._saveAs)
        self._catch(DirectEditDocument.In.ChangeID, self._changeID)
        self._catch(DocumentCache.Out.RequestedDocument, self._document)
        self._catch(DocumentCache.Out.DocumentChanged, self._changed)
        self._catch(DocumentCache.Out.DocumentSaved, self._saved)

        self._addRouting(DocumentChanger.Out.SelectionChanged, Viewer.In.Refresh)

    def _enable(self, enabled):
        self._throw(Editor.In.Enable, enabled)

    def _updateAll(self):
        self._throw(Viewer.In.Document, self._doc)

    def _changeID(self, pillow, newID):
        self._newID = newID

    def _load(self, pillow, feathers):
        if feathers == None and self._newID != None:
            feathers = self._newID

        if self._id == feathers: return

        self._throw(DocumentCache.In.DeleteShadowCopy, self._id)
        self._id = feathers

        self._enable(False)
        self._throw(DocumentCache.In.RequestDocument, self._id)

    def _saved(self, pillow, feathers):
        if feathers != self._id: return

        if self._requestNew:
            self._requestNew = False
            self._throw(DocumentCache.In.RequestDocument, self._id)
        else:
            self._throw(DocumentCache.In.CreateShadowCopy, self._doc.documentID)
            self._enable(True)

    def _saveAs(self, pillow, newID):
        if newID != None:
            self._newID = newID

        self._id = self._newID

        self._enable(False)

        if self._doc.documentID != self._id:
            self._requestNew = True
            self._throw(DocumentCache.In.StoreShadowCopyAs, (self._doc.documentID, self._id))
        else:
            self._throw(DocumentCache.In.StoreShadowCopy, self._doc.documentID)

    def _save(self, pillow, feathers):
        if self._newID != None:
            from twisted.internet import reactor
            reactor.callLater(0, self._saveAs, pillow, self._newID)
            return

        self._enable(False)
        self._throw(DocumentCache.In.StoreShadowCopy, self._doc.documentID)

    def _changed(self, pillow, doc):
        if doc.documentID != self._id: return 
        self._throw(DocumentCache.In.ReplaceShadowCopy, self._doc.documentID)

        self._updateAll() 

    def _document(self, pillow, doc):
        if doc.documentID != self._id: return 

        self._throw(DocumentCache.In.CreateShadowCopy, doc.documentID)

        self._doc = doc
        self._updateAll()
        self._enable(True)

    def initialize(self):
        self._throw(DocumentCache.In.RequestDocument, self._id)
        self._enable(False)
