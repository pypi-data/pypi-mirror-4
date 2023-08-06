# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

from twisted.internet import defer, threads, task
from collections import deque

def Callable(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(self, *args, **kw):
        from twisted.internet import reactor
        return task.deferLater(reactor, 0, self.lockedCall, fn, self, *args, **kw)
    return wrapper

class Service(object):
    def __init__(self):
        # lock queue
        self.__callables = deque()
        self.__lock = defer.DeferredLock()

    def __unlock(self, val):
        # print "Release lock"
        self.__lock.release()
        return val

    # call a synchronous function in an asynchronous manner 
    def lockedCall(self, f, *args, **kw):
        # add function and arguments to lock queue
        self.__callables.append( (f, args, kw) )

        # acquire lock and call the passed function with arguments 
        # print "Wait for lock"
        d = self.__lock.acquire()
        d.addCallback(self.__call)
        return d

    # call the next function with arguments in the lock queue
    def __call(self, _): 
        # print "Acquire Lock"
        f, args, kw = self.__callables.popleft()
        d = threads.deferToThread(f, *args, **kw)
        
        # unlock definitely (even on error)
        d.addBoth(self.__unlock)
        return d
