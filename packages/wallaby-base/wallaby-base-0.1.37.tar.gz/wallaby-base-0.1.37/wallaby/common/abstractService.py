# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

class AbstractService(object):
    def __init__(self, config):
        self._config = config

    def initialize(self):
        pass
