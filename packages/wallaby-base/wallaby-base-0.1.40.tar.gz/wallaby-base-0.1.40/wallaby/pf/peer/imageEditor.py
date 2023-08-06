# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from editor import Editor

class ImageEditor(Editor):
    def __init__(self, *args, **ka):
        Editor.__init__(self, *args)

    def _fieldChanged(self):
        name = value = None
        if self._valueCallback:
            value, name = self._valueCallback()

        print "try to save image", self._path, name

        if (self._document):
            self._document.set(self._path, name)

            if name:
                self._document.setAttachment(name, value)

        self._throwFieldChanged(self._path)
