# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from sm import *
import wallaby.FX as FX

from embeddedViewer import EmbeddedViewer
from documentChanger import DocumentChanger
from documentCache import DocumentCache
from multiViewer import MultiViewer
from database import Database
from viewer import Viewer
from editor import Editor

class EditDocument(SMPeer):
    Description = ("Provides a document edit/view logic", '{"alwaysEdit": false}')

    Load = Pillow.In
    LoadAndEdit = Pillow.In
    Edit = Pillow.In
    New = Pillow.In
    NewAndSave = Pillow.In
    Save = Pillow.In
    Remove = Pillow.In
    Rollback = Pillow.In
    Resolve = Pillow.In

    State = Pillow.OutState

    Dependencies = [
        "DocumentCache",
        "DocumentChanger"
    ]

    Sending = [
        Viewer.In.Document, 
        Viewer.In.Refresh, 
        MultiViewer.In.Refresh, 
        Editor.In.Conflict,
        Editor.In.Enable,
        DocumentCache.In.CreateShadowCopy,
        Database.In.CreateDocument,
        DocumentCache.In.RequestDocument,
        DocumentCache.In.StoreShadowCopy,
        DocumentCache.In.DeleteShadowCopy
    ]

    Receiving = [
        Database.Out.DocumentNotFound,
        Database.Out.DocumentDeleted,
        Database.Out.DocumentCreated,
        Editor.Out.FieldChanged,
        DocumentCache.Out.RequestedDocument,
        DocumentCache.Out.DoesNotExist,
        DocumentCache.Out.DocumentChanged,
        DocumentCache.In.DocumentCreated,
        DocumentCache.In.DocumentSaved
    ] 

    def __init__(self, room, **args):
        store = DocumentStore()
        states = []

        states.append(Undef(store, **args))
        states.append(Loading(store, **args))
        states.append(LoadingWillEdit(store, **args))
        states.append(Saving(store, **args))
        states.append(SavingNew(store, **args))
        states.append(View(store, **args))
        states.append(Edit(store, **args))
        states.append(Dirty(store, **args))
        states.append(Creating(store, **args))
        states.append(CreatingAndSave(store, **args))
        states.append(New(store, **args))

        SMPeer.__init__(self, room, EditDocument.Out.State, states, "Undef")

class DocumentStore:
    def __init__(self):
        self._documentID = None
        self._document = None

    @FX.Property
    def document():
        doc = "The document Property."
        def fget(self):
            return self._document
        def fset(self, value):
            self._document = value


    @FX.Property
    def documentID():
        doc = "The documentID Property."
        def fget(self):
            return self._documentID
        def fset(self, value):
            self._documentID = value

class Loadable:
    def __init__(self, **args):
        self._catch(EditDocument.In.Load, self._load)
        self._catch(EditDocument.In.LoadAndEdit, self._loadAndEdit)

        if not args.get("ignoreNotFound", False):
            self._setTransition(Database.Out.DocumentNotFound, "Undef")

        self._addRouting(Database.Out.DocumentCreated, MultiViewer.In.Refresh)
        self._addRouting(Database.Out.DocumentDeleted, MultiViewer.In.Refresh)

        self._config = args

    def _load(self, pillow, documentID):
        if documentID == None:
            self._switchState("Undef")
            return

        if 'alwaysEdit' in self._config and self._config['alwaysEdit']:
            self._switchState("LoadingWillEdit")
        else:
            self._switchState("Loading")

        self._store.documentID = documentID
        self._throw(DocumentCache.In.RequestDocument, self._store.documentID)

    def _loadAndEdit(self, pillow, documentID):
        if documentID == None:
            self._switchState("Undef")
            return

        if documentID == self._store.documentID and isinstance(self, Dirty):
            # already editing...
            # FX.debug("Skipping, because already in edit mode")
            return

        self._switchState("LoadingWillEdit")
        self._store.documentID = documentID
        self._throw(DocumentCache.In.RequestDocument, self._store.documentID)

    def _stateSwitched(self):
        self._throw(Viewer.In.Document, None)
        self._throw(Editor.In.Enable, False)

    def _create(self, pillow, feathers):
        self._switchState("Creating")

        from twisted.internet import reactor
        reactor.callLater(0, self.__create, pillow, feathers)

    def _createAndSave(self, pillow, feathers):
        self._switchState("CreatingAndSave")

        from twisted.internet import reactor
        reactor.callLater(0, self.__create, pillow, feathers)

    @defer.inlineCallbacks
    def __create(self, pillow, feathers):
        if isinstance(feathers, str) or isinstance(feathers, unicode):
            try:
                feathers = yield DocumentChanger.transform(None, feathers)
            except Exception as e:
                feathers = None
                print "ERROR - Exception: " + str(e)

        if type(feathers) is dict:
            self._throw(Database.In.CreateDocument, feathers)
        else:
            self._throw(Database.In.CreateDocument, None)

class OnShadowCopy:
    def __init__(self, **args):
        self._catch(EditDocument.In.Save, self._save)
        self._catch(DocumentCache.Out.DocumentChanged, self._docChanged)

    def _docChanged(self, pillow, doc):
        if doc.documentID != self._store.documentID:
            return

        if isinstance(self, (Dirty, New)) and not isinstance(self, Edit):
            self._throw(Editor.In.Conflict, doc)
        else:
            if 'alwaysEdit' in self._config and self._config['alwaysEdit']:
                self._switchState("LoadingWillEdit")
            else:
                self._switchState("Loading")

            self._store.documentID = doc.documentID
            self._throw(DocumentCache.In.RequestDocument, doc.documentID)

    def _stateSwitched(self):
        self._throw(Editor.In.Enable, True)

    def _save(self, *args):
        self._switchState("Saving")
        self._throw(DocumentCache.In.StoreShadowCopy, self._store.documentID)

class Undef(Loadable, State):
    def __init__(self, store, **args):
        State.__init__(self)
        Loadable.__init__(self, **args)
        self._store = store
        self._catch(EditDocument.In.New, self._create)
        self._catch(EditDocument.In.NewAndSave, self._createAndSave)

    def _stateSwitched(self):
        Loadable._stateSwitched(self)

class Loading(Loadable, State):
    def __init__(self, store, **args):
        State.__init__(self)
        Loadable.__init__(self, **args)
        self._store = store
        self._catch(DocumentCache.Out.RequestedDocument, self._document)
        if 'alwaysEdit' in args and args['alwaysEdit']:
            self._setTransition(DocumentCache.Out.RequestedDocument, "Edit")
        else:
            self._setTransition(DocumentCache.Out.RequestedDocument, "View")

    def _stateSwitched(self):
        self._throw(Editor.In.Enable, False)

    def _document(self, pillow, document):
        if self._store.documentID == document.documentID:
            self._store.document = document
            self._throw(Viewer.In.Document, document)

class LoadingWillEdit(Loadable, State):
    def __init__(self, store, **args):
        State.__init__(self)
        Loadable.__init__(self, **args)
        self._store = store
        self._catch(DocumentCache.Out.RequestedDocument, self._document)
        self._setTransition(DocumentCache.Out.RequestedDocument, "Edit")

    def _stateSwitched(self):
        self._throw(Editor.In.Enable, False)

    def _document(self, pillow, document):
        if self._store.documentID == document.documentID:
            self._throw(DocumentCache.In.ReplaceShadowCopy, self._store.documentID)
            self._store.document = document
            self._throw(Viewer.In.Document, document)

class Saving(OnShadowCopy, State):
    def __init__(self, store, **args):
        State.__init__(self)
        OnShadowCopy.__init__(self, **args)
        self._store = store
        self._config = args
        self._catch(DocumentCache.Out.DocumentSaved, self._documentSaved)

    def _stateSwitched(self):
        self._throw(Editor.In.Enable, False)

    def _documentSaved(self, pillow, documentID):
        if self._store.documentID == documentID:
            if 'alwaysEdit' in self._config and self._config['alwaysEdit']:
                self._throw(DocumentCache.In.CreateShadowCopy, self._store.documentID)
                self._switchState("Edit")
            else:
                self._switchState("View")

class SavingNew(Saving):
    def _documentSaved(self, pillow, documentID):
        Saving._documentSaved(self, pillow, documentID)
        if self._store.documentID == documentID:
            self._throw(DocumentCache.In.RequestDocument, self._store.documentID)
            self._throw(MultiViewer.In.Refresh, self._store.documentID)

class View(Loading):
    def __init__(self, store, **args):
        Loading.__init__(self, store, **args)
        self._catch(DocumentCache.Out.DocumentChanged, self._document)
        self._catch(EditDocument.In.Edit, self._edit)
        self._catch(EditDocument.In.New, self._create)
        self._catch(EditDocument.In.NewAndSave, self._createAndSave)
        self._catch(EditDocument.In.Remove, self._remove)
        self._addRouting(EmbeddedViewer.Out.SelectionChanged, Viewer.In.Refresh)
        self._addRouting(DocumentChanger.Out.SelectionChanged, Viewer.In.Refresh)

    def _stateSwitched(self):
        self._throw(Editor.In.Enable, False)

    def _edit(self, *args):
        self._switchState("Edit")
        self._throw(DocumentCache.In.CreateShadowCopy, self._store.documentID)

    def _remove(self, *args):
        self._switchState("Undef")
        self._throw(DocumentCache.In.DeleteDocument, self._store.documentID)

class Dirty(OnShadowCopy, State):
    def __init__(self, store, **args):
        State.__init__(self)
        OnShadowCopy.__init__(self, **args)
        self._store = store
        self._config = args

        self._catch(EditDocument.In.Rollback, self._rollback)
        self._catch(EditDocument.In.Resolve, self._resolve)
        self._addRouting(Editor.Out.FieldChanged, Viewer.In.Refresh)

        self._addRouting(EmbeddedViewer.Out.SelectionChanged, Viewer.In.Refresh)
        self._addRouting(DocumentChanger.Out.SelectionChanged, Viewer.In.Refresh)

    def _resolve(self, *args):
        if self._store.document:
            self._store.document.resolve()
            self._save(*args)

    def _rollback(self, *args):
        self._switchState("View")
        self._throw(DocumentCache.In.DeleteShadowCopy, self._store.documentID)

        if 'alwaysEdit' in self._config and self._config['alwaysEdit']:
            self._throw(EditDocument.In.LoadAndEdit, self._store.documentID)
        else:
            self._throw(EditDocument.In.Load, self._store.documentID)

class Edit(Dirty, Loadable):
    def __init__(self, store, **args):
        Dirty.__init__(self, store, **args)
        Loadable.__init__(self, **args)
        self._addRouting(Editor.Out.FieldChanged, Viewer.In.Refresh)
        self._setTransition(Editor.Out.FieldChanged, "Dirty")
        self._setTransition(DocumentCache.Out.DoesNotExist, "Undef")

        if 'alwaysEdit' in args and args['alwaysEdit']:
            self._catch(EditDocument.In.New, self._create)
            self._catch(EditDocument.In.NewAndSave, self._createAndSave)
            self._catch(EditDocument.In.Remove, self._remove)

    def _remove(self, *args):
        self._switchState("Undef")
        self._throw(DocumentCache.In.DeleteDocument, self._store.documentID)

class Creating(State):
    def __init__(self, store, **args):
        State.__init__(self)
        self._store = store
        self._catch(DocumentCache.Out.DocumentCreated, self._new)
        self._addRouting(Editor.Out.FieldChanged, Viewer.In.Refresh)

    def _new(self, pillow, document):
        self._switchState("New")
        self._store.documentID = document.documentID
        self._throw(Viewer.In.Document, document)

class CreatingAndSave(State):
    def __init__(self, store, **args):
        State.__init__(self)
        self._store = store
        self._catch(DocumentCache.Out.DocumentCreated, self._new)

    def _new(self, pillow, document):
        self._switchState("SavingNew")
        self._store.documentID = document.documentID
        self._throw(DocumentCache.In.StoreShadowCopy, self._store.documentID)

class New(OnShadowCopy, State):
    def __init__(self, store, **args):
        State.__init__(self)
        OnShadowCopy.__init__(self, **args)
        self._store = store
        self._catch(EditDocument.In.Rollback, self._rollback)
        self._addRouting(Editor.Out.FieldChanged, Viewer.In.Refresh)

    def _save(self, *args):
        self._switchState("SavingNew")
        self._throw(DocumentCache.In.StoreShadowCopy, self._store.documentID)

    def _rollback(self, *args):
        self._switchState("Undef")
        self._throw(DocumentCache.In.DeleteShadowCopy, self._store.documentID)
