# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from editor import Editor

class BooleanEditor(Editor):
    def _fieldChanged(self):
        value = False
        if self._valueCallback:
            value = self._valueCallback()
        if (self._document):
            self._document.set(self._path, value) 

        self._throwFieldChanged()
