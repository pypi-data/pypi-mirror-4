# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from peer import *

from wallaby.pf.peer.viewer import Viewer

class ActionButtonPeer(Peer):

    Receiving = [
        Viewer.In.Document
    ]

    def __init__(self, room, pillow, feather, tab=None, otherPillows=None, translate=False):
        self.pillow = pillow
        self.feather = feather
        self._otherPillows = otherPillows
        self._translate = translate

        Peer.__init__(self, room)

        if tab != 'None':
            self.tab = tab
        else:
            self.tab = None

        self._doc = None

        if self._translate:
            self._catch(Viewer.In.Document, self._docArrived)

    def _docArrived(self, pillow, doc):
        self._doc = doc

    def dynamicPillows(self):
        if isinstance(self.pillow, (unicode, str)):
            return [self.pillow]
        else:
            return []

    def __translate(self, feathers):
        if feathers != None:
            import re
            if isinstance(feathers, (str, unicode)) and '%__path__:' in feathers:
                if self._doc is None: return None

                match = re.match('(.*?)%__path__:(.*?)%(.*)', feathers)
                return match.group(1) + self._doc.get(match.group(2)) + match.group(3)
            if isinstance(feathers, dict):
                import copy
                feathers = copy.deepcopy(feathers)
                for k, v in feathers.items():
                    if '%__path__:' in v:
                        if self._doc is None: return None

                        match = re.match('(.*?)%__path__:(.*?)%(.*)', v)
                        feathers[k] = match.group(1) + self._doc.get(match.group(2)) + match.group(3)

                return feathers
            
        return feathers 

    def buttonClicked(self, feather=None):
        if self.feather is not None: 
            if not isinstance(self.feather, (unicode, str)) or len(self.feather) > 0: feather = self.feather 

        if self._translate: feather = self.__translate(feather)
            
        self._throw(self.pillow, feather)

        if self._otherPillows:
            for pillow in self._otherPillows:
                _feather = None

                if ';' in pillow:
                    pillow, _feather = pillow.split(';')

                if _feather is None and feather is not None: _feather = feather

                if self._translate: _feather = self.__translate(_feather)

                self._throw(pillow, _feather)

        if self.tab:
            room = self._roomName
            tab = self.tab
            if ":" in tab:
                room, tab = tab.split(":")

            from tab import Tab
            self._throw(room + ":" + Tab.In.Select, tab)
