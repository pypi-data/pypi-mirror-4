#!/usr/bin/env python
#initializer.py
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
    sys.exit('Error initializing twisted.internet.reactor in initializer.py')
from twisted.internet.defer import Deferred, maybeDeferred
from twisted.internet.task import LoopingCall

import lib.dhnio as dhnio
from lib.automat import Automat
import lib.automats as automats

import network_connector
import p2p_connector
import installer
import shutdowner

import dhninit
import webcontrol

_Initializer = None

#------------------------------------------------------------------------------

def A(event=None, arg=None, use_reactor=True):
    global _Initializer
    if _Initializer is None:
        _Initializer = Initializer('initializer', 'AT_STARTUP', 2)
    if event is not None:
        if use_reactor:
            _Initializer.automat(event, arg)
        else:
            _Initializer.event(event, arg)
    return _Initializer


class Initializer(Automat):
    
    def init(self):
        self.flagCmdLine = False
        self.is_installed = None
    
    def state_changed(self, oldstate, newstate):
        automats.set_global_state('INIT ' + newstate)

    def A(self, event, arg):
        #---AT_STARTUP---
        if self.state == 'AT_STARTUP':
            if event == 'run':
                self.doInitLocal(arg)
                self.flagCmdLine = False
                shutdowner.A('init')
                self.state = 'LOCAL'
            elif event == 'run-cmd-line-register':
                self.flagCmdLine = True
                installer.A('register-cmd-line', arg)
                shutdowner.A('init')
                shutdowner.A('ready')
                self.state = 'INSTALL'
            elif event == 'run-cmd-line-recover':
                self.flagCmdLine = True
                installer.A('recover-cmd-line', arg)
                shutdowner.A('init')
                shutdowner.A('ready')
                self.state = 'INSTALL'
        #---LOCAL---
        elif self.state == 'LOCAL':
            if event == 'init-local-done' and self.isInstalled():
                self.doInitContacts()
                self.state = 'CONTACTS'
            elif event == 'init-local-done' and not self.isInstalled() and self.isGUIPossible():
                self.doShowGUI()
                installer.A('init')
                self.doUpdate()
                shutdowner.A('ready')
                self.state = 'INSTALL'
            elif event == 'init-local-done' and not self.isInstalled() and not self.isGUIPossible():
                shutdowner.A('stop')
                self.state = 'STOPPING'
        #---CONTACTS---
        elif self.state == 'CONTACTS':
            if event == 'init-contacts-done':
                self.doInitConnection()
                network_connector.A('init')
                p2p_connector.A('init')
                self.doShowGUI()
                self.doUpdate()
                shutdowner.A('ready')
                self.state = 'CONNECTION'
            elif event == 'shutdowner.state' and arg is 'FINISHED':
                self.doDestroyMe()
                self.state = 'EXIT'
        #---CONNECTION---
        elif self.state == 'CONNECTION':
            if event == 'p2p_connector.state' and arg in ['CONNECTED', 'DISCONNECTED']:
                self.doInitModules()
                self.doUpdate()
                self.state = 'MODULES'
            elif event == 'shutdowner.state' and arg is 'FINISHED':
                self.doDestroyMe()
                self.state = 'EXIT'
        #---MODULES---
        elif self.state == 'MODULES':
            if event == 'init-modules-done':
                self.doUpdate()
                self.state = 'READY'
            elif event == 'shutdowner.state' and arg is 'FINISHED':
                self.doDestroyMe()
                self.state = 'EXIT'
        #---INSTALL---
        elif self.state == 'INSTALL':
            if not self.flagCmdLine and event == 'installer.state' and arg == 'DONE':
                self.doInitContacts()
                self.doUpdate()
                self.state = 'CONTACTS'
            elif self.flagCmdLine and event == 'installer.state' and arg == 'DONE':
                shutdowner.A('stop')
                self.state = 'STOPPING'
            elif event == 'shutdowner.state' and arg is 'FINISHED':
                self.doDestroyMe()
                self.state = 'EXIT'
        #---READY---
        elif self.state == 'READY':
            if event == 'shutdowner.state' and arg is 'FINISHED':
                self.doDestroyMe()
                self.state = 'EXIT'
        #---STOPPING
        elif self.state == 'STOPPING':
            if event == 'shutdowner.state' and arg is 'FINISHED':
                self.doDestroyMe()
                self.state = 'EXIT'
        #---EXIT---
        elif self.state == 'EXIT':
            pass

    def isInstalled(self):
        if self.is_installed is None:
            self.is_installed = dhninit.check_install() 
        return self.is_installed
    
    def isGUIPossible(self):
        if dhnio.Windows():
            return True
        if dhnio.Linux():
            return dhnio.X11_is_running()
        return False

    def doUpdate(self):
        webcontrol.OnUpdateStartingPage()

    def doInitLocal(self, arg):
        maybeDeferred(dhninit.init_local, arg).addCallback(
            lambda x: self.automat('init-local-done'))

    def doInitContacts(self):
        dhninit.init_contacts(
            lambda x: self.automat('init-contacts-done'),
            #lambda x: self.automat('init-contacts-failed'), )
            lambda x: self.automat('init-contacts-done'), )

    def doInitConnection(self):
        dhninit.init_connection()

    def doInitModules(self):
        maybeDeferred(dhninit.init_modules).addCallback(
            lambda x: self.automat('init-modules-done'))

    def doShowGUI(self):
        d = webcontrol.init()
        if dhninit.UImode == 'show' or not self.is_installed: 
            d.addCallback(webcontrol.show)
        webcontrol.ready()

    def doDestroyMe(self):
        global _Initializer
        del _Initializer
        _Initializer = None
        automats.get_automats_by_index().pop(self.index)




