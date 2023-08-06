# Copyright (c) by it's authors. 
# Some rights reserved. See LICENSE, AUTHORS.

import twisted.application.service
from twisted.python import logfile
import wallaby.FX as FX
import twisted.python.log as log
import os

class FXLogger(twisted.application.service.Service):
    def __init__(self, logName=None, logDir="./log/"):
        self.logName = logName
        self.logDir = logDir
        self.maxLogSize = 1000000
        self.pidfile = None

    def setPIDFile(self, pidfile):
        self.pidfile = pidfile
       
    def startService(self):
        if self.logName and os.path.exists(self.logDir):
            self.logFile = logfile.LogFile(self.logName, self.logDir, rotateLength=self.maxLogSize)
            self.errlog = log.FileLogObserver(self.logFile)
            self.errlog.start(  )

        if self.pidfile:
	    # self.pidfile = 'c:/test2.pid'
            print "Writing pid", os.getpid(), "to pidfile:", (">" + self.pidfile + "<")
            f = open(self.pidfile, "w+")
            f.write(str(os.getpid()))
            f.close()
        
    def stopService(self):
        if self.logName:
            self.errlog.stop(  )
            self.logFile.close(  )

	if self.pidfile:
            if os.path.isfile(self.pidfile):
                os.remove(self.pidfile)



