# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

import wallaby.FX as FX
from twisted.internet import defer
from twisted.internet import task

class QueryResult(object):
    def __init__(self, source, query):
        self.query = query
        self._source = source

    def __str__(self):
        return "<"+self.__class__.__name__+"("+hex(id(self))+") with "+str(self.length())+" entries>"

    def source(self):
        return self._source

    def identifier(self):
        if self.query == None:
            return None
        else:
            return self.query.get('identifier')

    def deferredGetValue(self, index, path):
        return None

    def reorder(self, row, i1, i2):
        return None

    def deferredGetDocument(self, index):
        return None

    def deferredGetValues(self, indexList, path):
        values = []
        for index in indexList:
            values.append(self.deferredGetValue(index, path))
        return values

    def getDocumentID(self, index):
        return None

    def getDocumentIDs(self, indexList):
        documentIDs = []
        for index in indexList:
            documentIDs.append(self.getDocumentID(index))
        return documentIDs

    def length(self):
        return -1

    @FX.Property                                                                                                                                      
    def query():
        doc = "The query Property."
        def fget(self):
            return self._query
        def fset(self, value):
            self._query = value

