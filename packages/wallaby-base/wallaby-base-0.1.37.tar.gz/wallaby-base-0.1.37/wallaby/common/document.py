# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from uuid import uuid4
import wallaby.FX as FX
from wallaby.common.pathHelper import PathHelper

class Document:
    def __init__(self, documentID=None, data=None):
        if data == None:
            if documentID == None:
                documentID = uuid4().hex
            data = {'_id':documentID}
        else:
            if documentID != None:
                data['_id'] = documentID
            elif '_id' in data:
                documentID = data['_id']
            else:
                documentID = uuid4().hex
                data['_id'] = documentID

        self._data = data
        self.documentID = documentID
        self.selection = {}

    def __str__(self):
        # return "<"+self.__class__.__name__+"("+hex(id(self))+") with id: '"+self.documentID+"'>"
        if self.documentID != None:
            if len(self.documentID) == 32:
                return "<"+self.__class__.__name__+"(..."+self.documentID[28:32]+")>"
            return "<"+self.__class__.__name__+"("+self.documentID+")>"
        return "<"+self.__class__.__name__+"(None)>"

    def hasConflicts(self):
        return False

    def getConflicts(self):
        return None

    def changes(self, doc):
        return []

    def getFlat(self, path):
        if path not in self._data:
            return None
        else:
            return self._data[path]

    def get(self, path, **kw):
        return PathHelper.getValue(self._data, path, self.selection, **kw)

    def getSelection(self, path):
        return PathHelper.getSelection(path, self.selection)

    def sub(self, key, path=None, dct=None):
        if dct == None: dct = {} 

        if isinstance(key, dict):
            for k,v in key.items():
                subpath = k
                if path != None: subpath = path + "." + k

                self.sub(v, subpath, dct)
        else:
            PathHelper.setValue(dct, path, PathHelper.getValue(self._data, path))

        return dct

    def getDictionary(self):
        dict = copy.copy(self._data)
        if '_id' in dict:
            del dict['_id']
        if '_rev' in dict:
            del dict['_rev']
        if 'wallabyUser' in dict:
            del dict['wallabyUser']

        return dict

    def rev(self):
        return self._data.get("_rev", None)

    def set(self, path, value):
        return PathHelper.setValue(self._data, path, value, self.selection)

    def overwrite(self, path, value):
        return PathHelper.setValue(self._data, path, value, self.selection, recurse=True)

    def merge(self, path, value):
        return PathHelper.setValue(self._data, path, value, self.selection, merge=True)


    def select(self, path, index):
        PathHelper.setValue(self.selection, path + "._selection", index)

    def solveConflicts(self, document):
        pass

    def __deepcopy__(self, memo):
        doc = Document()
        doc.documentID = self.documentID
        doc.selection = self.selection

        import copy
        doc._data = copy.deepcopy(self._data)
        return doc

    def clone(self):
        doc = Document()
        doc.documentID = self.documentID
        doc.selection = self.selection
        doc._data = copy.deepcopy(self._data)
        return doc

    def resetDocumentID(self, id=None):
        if id == None:
            id = uuid4().hex

        self.documentID = id
        self._data['_id'] = id
        if '_rev' in self._data:
            del self._data['_rev']

    def deferredGetAttachment(self, name): #TODO: Not really deferred?
        # Hack for dummy images
        try:
            import os
            f = open('./tmp/' + name)
            size = os.fstat(f.fileno()).st_size
        except:
            return None, 0

    def setAttachment(self, name, attachment):
        f = open('./tmp/' + name, "w")
        f.write(attachment)
        f.close()

    def deleteAttachment(self, name):
        pass

    @FX.Property                                                                                                                                      
    def documentID():
        doc = "The documentID Property."
        def fget(self):
            return self._documentID
        def fset(self, value):
            self._documentID = value

    @FX.Property                                                                                                                                      
    def selection():
        doc = "The selection Property."
        def fget(self):
            return self._selection
        def fset(self, value):
            self._selection = value
