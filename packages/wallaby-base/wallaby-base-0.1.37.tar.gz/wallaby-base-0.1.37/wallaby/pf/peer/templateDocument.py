# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from directEditDocument import DirectEditDocument

from editor import Editor

class TemplateDocument(DirectEditDocument):

    Sending = [
        Editor.Out.FieldChanged
    ]

    def __init__(self, room, id=None, path=None, proto=None):
        DirectEditDocument.__init__(self, room, id)
        
        self._editDoc = None
        self._path = path
        self._proto = proto

        from viewer import Viewer
        self._catch(Viewer.In.Document, self._editDocChanged)

    def _editDocChanged(self, pillow, doc):
        self._editDoc = doc
        self._id = None

    def _enable(self, enabled):
        pass

    def _saveAs(self, pillow, newID):
        if self._doc == None:
            newDoc = self._editDoc.clone()
            newDoc.resetDocumentID(newID)
            newDoc.overwrite(None, self._proto)

            from documentCache import DocumentCache
            self._throw(DocumentCache.In.CreateAndSaveDocument, newDoc._data)
            return

        self._doc.set(self._path, self._editDoc.get(self._path))
        DirectEditDocument._saveAs(self, pillow, newID)

    def _updateAll(self):
        if self._editDoc is None or self._doc is None: return

        if self._path is not None:
            self._editDoc.set(self._path, self._doc.get(self._path))

            path = Editor.translatePath(self._editDoc, self._path)
            self._throw(Editor.Out.FieldChanged, path)
        else:
            id = self._editDoc.get('_id')
            rev = self._editDoc.get('_rev')

            self._editDoc._data = copy.deepcopy(self._doc._data)
            self._editDoc.set('_id', id)
            if rev is not None: self._editDoc.set('_rev', rev)

            self._throw(Editor.Out.FieldChanged, "")

    def initialize(self):
        pass
