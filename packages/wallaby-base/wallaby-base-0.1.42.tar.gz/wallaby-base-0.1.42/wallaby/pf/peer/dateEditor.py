# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from editor import Editor

class DateEditor(Editor):
    def _fieldChanged(self):
        from wallaby.common.pathHelper import SelectionNotSpecified

        value = None
        if self._valueCallback:
            value = self._valueCallback()
        if (self._document):
            try:
                self._document.set(self._path, value) 
                self._throwFieldChanged(self._path)
            except SelectionNotSpecified as e:
                self._setReadOnly(True)

