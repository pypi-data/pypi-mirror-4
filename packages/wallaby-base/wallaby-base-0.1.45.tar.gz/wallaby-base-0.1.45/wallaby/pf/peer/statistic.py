# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

class Statistic(Peer):
    #Sending pillows
    MessagesSinceLastReport = Pillow.Out

    def __init__(self, room, pillow="*", delay=1.0):
        Peer.__init__(self, room)
        self._delay = delay
        self._count = 0
        self._catch(pillow, self._message)

        self._initialized = False

    def initialize(self):
        if self._initialized: return
        self._initialized = True

        self._triggerReport()
        import time

    def _triggerReport(self):
        from twisted.internet import reactor, task
        task.deferLater(reactor, self._delay, self._sendReport)

    def _sendReport(self):
        self._throw(Statistic.Out.MessagesSinceLastReport, self._count)
        self._count = 0
        self._triggerReport()

    def _message(self, pillow, feathers):
        self._count += 1
