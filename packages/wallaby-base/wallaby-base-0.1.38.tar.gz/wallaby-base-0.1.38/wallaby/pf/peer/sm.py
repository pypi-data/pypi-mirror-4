# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

class SMPeer(Peer):
    def __init__(self, room, statePillow, states=[], initState="Start"):
        Peer.__init__(self, room)
        self._routings = set()
        self._transitions = set()
        self._callbacks = set()
        self._states = {} #Name->State
        self._statePillow = statePillow
        self._initState = initState

        if len(states) > 0:
            self._state = states[0]
        else:
            pass #TODO: Throw exception

        for state in states:
            self._states[state._name] = state
            state._setStateMachine(self)

        for pillow in self._callbacks:
            self._catch(pillow, self._callback)

        for pillow in self._routings:
            self._catch(pillow, self._routePillow)

        for pillow in self._transitions:
            self._catch(pillow, self._transitionState)

    def initialize(self):
        self.switchState(self._initState)

    def addRoutings(self, pillows):
        self._routings = self._routings.union(set(pillows))

    def addTransitions(self, pillows):
        self._transitions = self._transitions.union(set(pillows))

    def addCallbacks(self, pillows):
        self._callbacks = self._callbacks.union(set(pillows))

    def _routePillow(self, *args):
        self._state._routePillow(*args)

    def _transitionState(self, *args):
        self._state._transitionState(*args)

    def _callback(self, *args):
        self._state._callback(*args)

    def switchState(self, stateName):
        # Already in correct state
        if self._state != None and self._state._name == stateName: return

        # print "Switch to state", stateName, "in context", self._contextName
        if stateName in self._states:
            self._state = self._states[stateName]
            self._throw(self._statePillow, stateName)
            self._state._stateSwitched()

class State:
    def __init__(self, name=None):
        if name:
            self._name = name
        else:
            self._name = self.__class__.__name__

        self._stateMachine = None
        self._routings = {}
        self._transitions = {}
        self._callbacks = {}
        self._localCallbacks = {}

    def _stateSwitched(self):
        pass

    def _addRouting(self, sourcePillow, destinationPillow):
        if not sourcePillow in self._routings:
            self._routings[sourcePillow] = set()
        self._routings[sourcePillow].add(destinationPillow)

    def _setTransition(self, pillow, destinationState):
        self._transitions[pillow] = destinationState

    def _catch(self, pillow, callback):

        if not pillow in self._callbacks:
            self._callbacks[pillow] = set()

        self._callbacks[pillow].add(callback)

        if ':' in str(pillow): 
            room, pillow = pillow.split(':')

        if not pillow in self._localCallbacks:
            self._localCallbacks[pillow] = set()

        self._localCallbacks[pillow].add(callback)

    def sm(self):
        return self._stateMachine

    def _setStateMachine(self, stateMachine):
        self._stateMachine = stateMachine
        self._stateMachine.addRoutings(self._routings.keys())
        self._stateMachine.addTransitions(self._transitions.keys())
        self._stateMachine.addCallbacks(self._callbacks.keys())

    def _throw(self, pillow, feathers):
        self._stateMachine._throw(pillow, feathers, self)

    def _switchState(self, state):
        self._stateMachine.switchState(state)

    def _routePillow(self, pillow, feathers):
        if pillow in self._routings:
            for routing in self._routings[pillow]:
                self._throw(routing, feathers)

    def _transitionState(self, pillow, feathers):
        if pillow in self._transitions:
            self._switchState(self._transitions[pillow])

    def _callback(self, pillow, feathers):
        if pillow in self._localCallbacks:
            for callback in self._localCallbacks[pillow]:
                callback(pillow, feathers)
