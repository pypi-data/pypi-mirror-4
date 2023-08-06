# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

from viewer import Viewer
from editor import Editor

class SearchDocument(Peer):

    #Receiving pillows:
    Search = Pillow.In

    Sending = [
        Viewer.In.Document
    ]

    Routings = [
        (Editor.Out.FieldChanged, Viewer.In.Refresh)
    ]

    def __init__(self, searchRoom, resultRoom=None, document=None, identifier=None, appendWildcard=False):
        Peer.__init__(self, searchRoom)

        if not resultRoom:
            resultRoom = searchRoom
        self._resultRoom = resultRoom

        self._identifier = identifier
        self._appendWildcard = appendWildcard

        if document:
            self._document = document
        else:
            from wallaby.common.queryDocument import QueryDocument
            self._document = QueryDocument()

        self._document.set('identifier', self._identifier)
        self._document.set('query', '*')

        self._catch(SearchDocument.In.Search, self._search)
    
    
    def initialize(self):
        # set search field editable
        self._throw(Viewer.In.Document, self._document)
        self._throw(Editor.In.Enable, True)

    def _search(self, pillow, feathers):
        query = self._document.get('query')
        if self._appendWildcard and (len(query) == 0 or query[-1] != "*"):
            self._document.set('query', query + "*")

        from abstractQuery import AbstractQuery
        self._throw(self._resultRoom+":"+AbstractQuery.In.Query, self._document)
