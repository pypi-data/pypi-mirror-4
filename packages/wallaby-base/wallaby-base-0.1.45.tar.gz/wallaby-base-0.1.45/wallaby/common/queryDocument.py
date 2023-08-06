# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from document import Document
from wallaby.common.pathHelper import PathHelper

class QueryDocument (Document):
    def __init__(self, data = None):
        Document.__init__(self, "query")
        if data == None: data = {}
        self._data = data

    def get(self, path, **ka):
        return PathHelper.getValue(self._data, path, **ka)

    def set(self, path, value):
        return PathHelper.setValue(self._data, path, value)

    def merge(self, path, value):
        return PathHelper.setValue(self._data, path, value, merge=True)

    def identifier(self):
        return self.get("identifier")
