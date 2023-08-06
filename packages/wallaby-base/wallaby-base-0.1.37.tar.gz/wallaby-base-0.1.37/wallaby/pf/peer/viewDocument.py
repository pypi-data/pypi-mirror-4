# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

from editDocument import EditDocument
from documentCache import DocumentCache
from embeddedViewer import EmbeddedViewer
from documentChanger import DocumentChanger
from viewer import Viewer

class ViewDocument(Peer):
    Description = "View a document from the document cache"

    Routings = [
        (EmbeddedViewer.Out.SelectionChanged, Viewer.In.Refresh),
        (DocumentChanger.Out.SelectionChanged, Viewer.In.Refresh)
    ]

    Receiving = [
        EditDocument.In.Load,
        DocumentCache.Out.RequestedDocument,
        DocumentCache.Out.DocumentChanged
    ]

    Sending  = [
        Viewer.In.Document,
        EditDocument.Out.State,
        DocumentCache.In.RequestDocument
    ]

    Dependencies = [
        "DocumentCache",
        "DocumentChanger"
    ]

    def __init__(self, room):
        Peer.__init__(self, room)
        self._catch(EditDocument.In.Load, self._load)
        self._catch(DocumentCache.Out.RequestedDocument, self._document)
        self._catch(DocumentCache.Out.DocumentChanged, self._document)
        self._id = None

    def _load(self, pillow, docid):
        if docid == None:
            self._throw(Viewer.In.Document, None)
            self._throw(EditDocument.Out.State, 'Undef')
            return

        self._id = docid
        self._throw(DocumentCache.In.RequestDocument, docid)
        self._throw(EditDocument.Out.State, 'View')

    def _document(self, pillow, doc):
        from wallaby.common.document import Document
        if doc and isinstance(doc, Document) and doc.documentID == self._id:
            self._throw(Viewer.In.Document, doc)

    def initialize(self):
        self._throw(Viewer.In.Document, None)
        self._throw(EditDocument.Out.State, 'Undef')



