# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from multiViewer import MultiViewer

class IncrementalMultiViewer(MultiViewer):
    def __init__(self, *args, **ka):
        MultiViewer.__init__(self, *args, **ka)

        self._dct = {}
        self._IDs = []

    def _insertItems(self, f, elems):
        if self._delegate:
            self._delegate.beginInsertCB(f, len(elems))

        i = f
        for _id in elems:
            self._IDs.insert(i, _id)
            if _id in self._dct: self._dct[_id] += 1
            else: self._dct[_id] = 1
            i = i + 1

        if self._delegate:
            self._delegate.endInsertCB(f, len(elems))

    def _deleteItems(self, f, t):
        if self._delegate:
            self._delegate.beginDeleteCB(f, t)

        for i in range(f, t):
            if self._IDs[f] in self._dct:
                self._dct[self._IDs[f]] -= 1
                if self._dct[self._IDs[f]] == 0:
                    del self._dct[self._IDs[f]]
            else:
                print 'Error: Maybe duplicated entry in view'
            self._IDs.pop(f)

        if self._delegate:
            self._delegate.endDeleteCB(f, t)

    def _updateData(self, pillow, document):
        if document.documentID in self._IDs and self._delegate:
            self._delegate.updateCB(self._IDs.index(document.documentID))

   
    def _doRefreshData(self, queryResult):
        if queryResult:
            oldIDs = self._IDs

            self._queryResult = queryResult
            newIDs = queryResult.getDocumentIDs(range(queryResult.length()))

            c1 = len(oldIDs)
            c2 = len(newIDs)
            i1 = i2 = 0

            # print "View changed from", c1, "to", c2

            self._count = c2

            while i1 < c1 or i2 < c2:
                # not at end of any list
                if i1 < c1 and i2 < c2:
                    # item inserted
                    if oldIDs[i1] != newIDs[i2]:
                        if newIDs[i2] in self._dct:
                            self._deleteItems(i1, i1+1)
                            c1 = c1 - 1
                        else:
                            self._insertItems(i1, [newIDs[i2]])
                            i2 = i2 + 1
                            i1 = i1 + 1
                            c1 = c1 + 1
                    else:
                        if self._delegate:
                            self._delegate.updateCB(i1)
                        i2 = i2 + 1
                        i1 = i1 + 1

                # add item
                elif i2 < c2:
                    self._insertItems(i1, newIDs[i2:c2])
                    i2 = i2 + 1
                    i1 = i1 + 1
                    break

                # remove item
                elif i1 < c1:
                    self._deleteItems(i1, c1)
                    break

        if self._delegate:
            self._delegate.resetSelectionCB()
