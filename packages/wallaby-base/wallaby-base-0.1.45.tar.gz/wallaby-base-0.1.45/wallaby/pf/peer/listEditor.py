# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from editor import Editor

class ListEditor(Editor):
    def __init__(self, *args, **ka):
        Editor.__init__(self, *args, **ka)

    def _fieldChanged(self):
        value = False
        if self._valueCallback:
            checkBox = self._valueCallback()
            value = checkBox.value
            if (self._document):
                listVal = self._document.get(self._path)
                if checkBox.isChecked():
                    if isinstance(listVal, list) or isinstance(listVal, tuple):
                        if value not in listVal:
                            listVal.append(value)
                    else:
                        listVal = [value]
                    if value in ('true', 'True'):
                        listVal = True
                    elif value in ('false', 'False'):
                        listVal = False 
                        
                else:
                    if isinstance(listVal, list) or isinstance(listVal, tuple): 
                        for i in range(len(listVal)):
                            if listVal[i] == value:
                                listVal.pop(i)
                                break
                    else:
                        listVal = False

                    if value in ('true', 'True'):
                        listVal = False
                    elif value in ('false', 'False'):
                        listVal = True 

                self._document.set(self._path, listVal) 

        self._throwFieldChanged(self._path)
