# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

class DocumentCredentialsDatabase(Peer):
    from database import Database
    from documentCredentials import DocumentCredentials

    Routings = [
        (Database.Out.RequestedDocument, DocumentCredentials.In.RequestedDocument),
        (Database.Out.DocumentNotFound, DocumentCredentials.In.DocumentNotFound),
        (Database.Out.DocumentCreated, DocumentCredentials.In.DocumentCreated),
        (DocumentCredentials.Out.RequestDocument, Database.In.RequestDocument),
        (DocumentCredentials.Out.SaveDocument, Database.In.SaveDocument)
    ] 
    
    def __init__(self, room):
        Peer.__init__(self, room)
