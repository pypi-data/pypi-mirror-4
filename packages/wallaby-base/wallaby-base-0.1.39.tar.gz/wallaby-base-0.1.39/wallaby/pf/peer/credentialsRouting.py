# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

class CredentialsRouting(Peer):
    from credentialsConsumer import CredentialsConsumer
    from credentials import Credentials

    Routings = [
        (Credentials.Out.Credential, CredentialsConsumer.In.Credential)
    ]

    def __init__(self, room): Peer.__init__(self, room)
