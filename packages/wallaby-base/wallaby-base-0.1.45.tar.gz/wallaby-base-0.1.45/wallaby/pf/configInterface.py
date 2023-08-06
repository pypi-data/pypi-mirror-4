# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

class ConfigInterface(object):
    def getConfig(self, key=None, type=None): pass
    def setConfig(self, value, key=None, type=None): pass
    def resetConfig(self, key=None, type=None): pass
