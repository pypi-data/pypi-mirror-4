#!/usr/bin/env python
#shutdowner.py
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2012
#    All rights reserved.
#
#

import os
import sys

try:
    from twisted.internet import reactor
except:
    sys.exit('Error initializing twisted.internet.reactor in shutdowner.py')
from twisted.internet.defer import Deferred, maybeDeferred
from twisted.internet.task import LoopingCall

import lib.dhnio as dhnio
from lib.automat import Automat
import lib.automats as automats

import initializer
import dhninit

_Shutdowner = None

#------------------------------------------------------------------------------

def A(event=None, arg=None):
    global _Shutdowner
    if _Shutdowner is None:
        _Shutdowner = Shutdowner('shutdowner', 'AT_STARTUP', 2)
    if event is not None:
        _Shutdowner.event(event, arg)
    return _Shutdowner


class Shutdowner(Automat):
    
    def init(self):
        self.flagApp = False
        self.flagReactor = False
        self.shutdown_param = None
    
    def state_changed(self, oldstate, newstate):
        automats.set_global_state('SHUTDOWN ' + newstate)
        initializer.A('shutdowner.state', newstate)

    def A(self, event, arg):
        #---AT_STARTUP---
        if self.state == 'AT_STARTUP':
            if event == 'init':
                self.flagApp = False
                self.flagReactor = False
                self.state = 'INIT'
        #---INIT---
        elif self.state == 'INIT':
            if event == 'stop':
                self.shutdown_param = arg
                self.flagApp = True
            elif event == 'reactor-stopped':
                self.flagReactor = True
            elif event == 'ready' and self.flagReactor:
                self.state = 'FINISHED'
            elif event == 'ready' and not self.flagReactor and self.flagApp:
                self.doShutdown(self.shutdown_param)
                self.state = 'STOPPING'
            elif event == 'ready' and not self.flagReactor and not self.flagApp:
                self.state = 'READY'
        #---READY---
        elif self.state == 'READY':
            if event == 'stop':
                self.doShutdown(arg)
                self.state = 'STOPPING'
            elif event == 'reactor-stopped':
                self.state = 'FINISHED'
            elif event == 'block':
                self.state = 'BLOCKED'
        #---BLOCKED---
        elif self.state == 'BLOCKED':
            if event == 'stop':
                self.shutdown_param = arg
                self.flagApp = True
            elif event == 'reactor-stopped':
                self.flagReactor = True
            elif event == 'unblock' and not self.flagReactor and not self.flagApp:
                self.state == 'READY'
            elif event == 'unblock' and not self.flagReactor and self.flagApp:
                self.doShutdown(self.shutdown_param)
                self.state == 'STOPPING'
            elif event == 'unblock' and self.flagReactor:
                self.state == 'FINISHED'
        #---FINISHED
        elif self.state == 'FINISHED':
            pass

    def doShutdown(self, arg):
        if arg[0] == 'exit':
            dhninit.shutdown_exit()
        elif arg[0] == 'restart':
            dhninit.shutdown_restart(arg[1])





