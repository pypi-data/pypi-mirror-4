# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

from wallaby.pf.peer.database import Database
from wallaby.pf.peer.viewer import Viewer
from wallaby.pf.peer.editor import Editor
from wallaby.pf.pillow import Pillow
from wallaby.common.pathHelper import *
from twisted.internet import defer
from datetime import date, datetime
import copy, re

class DocumentChanger(Peer):
    Receiving = [
        Viewer.In.Document
    ]

    Sending = [
        Database.In.SaveDocument
    ]

    Change = Pillow.In
    Edit = Pillow.In
    Clone = Pillow.In
    SubClone = Pillow.In
    Embed = Pillow.In

    InsertRow = Pillow.In
    RemoveRow = Pillow.In

    InsertKey = Pillow.In
    RemoveKey = Pillow.In

    MoveUp = Pillow.In
    MoveDown = Pillow.In

    Select = Pillow.In

    SelectionChanged = Pillow.Out

    def __init__(self, room, dstRoom=None):
        Peer.__init__(self, room)
        self._document = None

        self._dstRoom = None

        if dstRoom != None: 
            from wallaby.pf.room import House
            self._dstRoom = House.get(dstRoom)

        self._catch(DocumentChanger.In.Change, self._change)
        self._catch(DocumentChanger.In.Edit, self._edit)
        self._catch(DocumentChanger.In.Clone, self._clone)
        self._catch(DocumentChanger.In.SubClone, self._subClone)
        self._catch(DocumentChanger.In.Embed, self._embed)
        self._catch(Viewer.In.Document, self._setDocument)

        self._catch(DocumentChanger.In.InsertRow, self._insertRow)
        self._catch(DocumentChanger.In.RemoveRow, self._removeRow)

        self._catch(DocumentChanger.In.InsertKey, self._insertKey)
        self._catch(DocumentChanger.In.RemoveKey, self._removeKey)

        self._catch(DocumentChanger.In.MoveUp, self._up)
        self._catch(DocumentChanger.In.MoveDown, self._down)

        self._catch(DocumentChanger.In.Select, self._select)

    #TODO: Add support for Enabler

    def _select(self, pillow, (path, idx) ):
        if not self._document: return

        path = path + ".*"
    
        try:
            currentIdx = PathHelper.getValue(self._document.selection, path + '._selection') 
            if currentIdx == idx: 
                # print path, ":", idx, "Already selected"
                return
        except:
            pass

        self._document.select(path, idx)
        path = path.replace('__root__.', '')
        self._throw(DocumentChanger.Out.SelectionChanged, path)

    def _up(self, pillow, path): 
        data = self._document.get(path, asList=True) 
        if data == None: return 

        sel = PathHelper.getValue(self._document.selection, path + '.*._selection') 
        if sel == None or sel == 0: return 
 
        data[sel-1], data[sel] = data[sel], data[sel-1]  
        self._throw(Editor.Out.FieldChanged, Editor.translatePath(self._document, path))

    def _down(self, pillow, path):
        data = self._document.get(path, asList=True)
        if data == None: return

        sel = PathHelper.getValue(self._document.selection, path + '.*._selection')
        if sel == None or sel == len(data)-1: return

        data[sel], data[sel+1] = data[sel+1], data[sel]
        self._throw(Editor.Out.FieldChanged, Editor.translatePath(self._document, path))
 
    def _embed(self, pillow, path):
        if not path or not self._document:
            return

        self._dstRoom.throw(DocumentChanger.In.InsertRow, (path, copy.deepcopy(self._document._data)) )

    def _subClone(self, pillow, doc):
        from twisted.internet import reactor
        reactor.callLater(0, self.__subClone, pillow, doc)

    def _insertKey(self, *args):
        self.__insert(*args, isList=False)

    def _removeKey(self, *args):
        self.__remove(*args, isList=False)

    def _insertRow(self, *args):
        self.__insert(*args, isList=True)

    def _removeRow(self, *args):
        self.__remove(*args, isList=True)

    def __insert(self, pillow, path, isList=True):
        if not path or not self._document:
            return

        doc = None
        key = '__new__'

        if isinstance(path, tuple) or isinstance(path, list):
            path, doc = path
        elif isinstance(path, dict):
            cfg = path
            path = cfg.get('path', None)
            key  = cfg.get('key', None)
            doc  = cfg.get('value', None)

        try:
            if isList:
                data = self._document.get(path, asList=True)
            else:
                data = self._document.get(path, asDict=True)
        except Exception as e:
            return

        if data == None:
            if isList:
                data = []
            else:
                data = {}

            try:
                self._document.set(path, data)
            except Exception as e:
                return

        if not isList and key in data:
            return

        try:
            sel = PathHelper.getValue(self._document.selection, path + '.*._selection')
        except SelectionNotSpecified:
            sel = None

        if sel == None:
            if isList:
                sel = len(data)
            else:
                sel = key

        #  print "__insert", sel, data

        if isList:
            data.insert(sel, doc)
        else:
            data[key] = doc

        self._document.select(path + '.*', sel) 
        self._throw(Editor.Out.FieldChanged, Editor.translatePath(self._document, path))

    def __remove(self, pillow, path, isList=True):
        if not path or not self._document:
            # TODO: debug out
            return

        if isList:
            data = self._document.get(path, asList=True)
        else:
            data = self._document.get(path, asDict=True)

        if data == None:
            # TODO: debug out
            return

        sel = PathHelper.getValue(self._document.selection, path + '.*._selection')
        if sel != None:
            del data[sel]
            self._throw(Editor.Out.FieldChanged, Editor.translatePath(self._document, path))

    @defer.inlineCallbacks
    def __subClone(self, pillow, feathers):
        if not feathers or not self._document:
            return

        path = feathers
        doc = None

        if ';' in feathers:
            path, doc = feathers.split(';')

        item = self._document.get(path)
        if not item: return

        from wallaby.common.document import Document
        newDoc = Document(data=copy.deepcopy(item))
        newDoc.resetDocumentID()

        if doc:
            yield DocumentChanger.transform(newDoc, doc)

        self._throw(Database.In.SaveDocument, (newDoc, None) )

    transformations = {
        "Y": lambda _: datetime.now().year,
        "M": lambda _: datetime.now().month,
        "D": lambda _: datetime.now().day,
        "h": lambda _: datetime.now().hour,
        "m": lambda _: datetime.now().minute,
        "s": lambda _: datetime.now().second
    } 

    @staticmethod
    def registerToken(token, callback):
        if token in DocumentChanger.transformations:
            print "ERROR - token", token, "already registered"
            return

        DocumentChanger.transformations[token] = callback

    @staticmethod
    def reregisterToken(token, callback):
        DocumentChanger.transformations[token] = callback

    @staticmethod
    def transform(newDoc, doc):
        if not doc:
            return False

        d = defer.Deferred()
        from twisted.internet import reactor
        reactor.callLater(0, DocumentChanger.__doTransform, d, newDoc, doc)
        return d

    @staticmethod
    @defer.inlineCallbacks
    def __doTransform(d, newDoc, doc):
        import json
        if isinstance(doc, (unicode, str)):
            while True:
                m = re.search(r"%(\w+)", doc)
                if m == None: break

                token = m.group(1)
                cb = DocumentChanger.transformations.get(m.group(1), lambda _: "null")

                from twisted.internet import reactor, task
                replacement = yield task.deferLater(reactor, 0, cb, newDoc)

                if not isinstance(replacement, str) and not isinstance(replacement, unicode):
                    replacement = json.dumps(replacement)

                doc = doc.replace('%' + token, unicode(replacement), 1)

            try:
                doc = json.loads(doc)
            except Exception as e:
                print "DocumentChanger", e
                d.errback("JSON error " + unicode(e) + " in: "+ doc)
                return

        if newDoc == None:
            newDoc = doc
        else:
            for key, val in doc.items():
                newDoc.set(key, val)

        d.callback(newDoc)

    def _clone(self, pillow, doc):
        from twisted.internet import reactor
        reactor.callLater(0, self.__clone, pillow, doc)

    @defer.inlineCallbacks
    def __clone(self, pillow, doc):
        if not doc or not self._document:
            return

        referenceID = None

        if ';' in doc:
            referenceID, doc = doc.split(';')

        newDoc = self._document.clone()
        newDoc.resetDocumentID()

        yield DocumentChanger.transform(newDoc, doc)

        if referenceID != None:
            newDoc.set(referenceID, self._document.documentID)

        self._throw(Database.In.SaveDocument, (newDoc, self._document) )

    def _change(self, pillow, doc):
        from twisted.internet import reactor
        reactor.callLater(0, self.__change, pillow, doc)

    def _edit(self, pillow, doc):
        from twisted.internet import reactor
        reactor.callLater(0, self.__edit, pillow, doc)

    def __edit(self, pillow, doc):
        if not doc or not self._document:
            return

        if not isinstance(doc, dict):
            try:
                import json
                doc = json.loads(doc)
            except Exception as e:
                print "JSON error " + unicode(e) + " in: "+ doc
                return

        for k, v in doc.items():
            self._document.set(k, v)
            self._throw(Editor.Out.FieldChanged, Editor.translatePath(self._document, k))

    @defer.inlineCallbacks
    def __change(self, pillow, doc):
        if not doc or not self._document:
            return

        newDoc = copy.deepcopy(self._document)
        yield DocumentChanger.transform(newDoc, doc)

        self._throw(Database.In.SaveDocument, (newDoc, self._document) )

    def _setDstDocument(self, pillow, document):
        self._dstDocument = document

    def _setDocument(self, pillow, document):
        self._document = document
