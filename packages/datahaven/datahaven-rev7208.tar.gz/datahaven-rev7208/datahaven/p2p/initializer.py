#!/usr/bin/env python
#initializer.py
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2012
#    Use of this software constitutes acceptance of the Terms of Use
#      http://datahaven.net/terms_of_use.html
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

import installer
import shutdowner
import network_connector
import p2p_connector

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
        if self.state is 'AT_STARTUP':
            if event == 'run' :
                self.doInitLocal(arg)
                self.flagCmdLine = False
                shutdowner.A('init')
                self.state = 'LOCAL'
            elif event == 'run-cmd-line-register' :
                self.flagCmdLine = True
                installer.A('register-cmd-line')
                shutdowner.A('init')
                shutdowner.A('ready')
                self.state = 'INSTALL'
            elif event == 'run-cmd-line-recover' :
                self.flagCmdLine = True
                installer.A('recover-cmd-line')
                shutdowner.A('init')
                shutdowner.A('ready')
                self.state = 'INSTALL'
        #---LOCAL---
        elif self.state is 'LOCAL':
            if event == 'init-local-done' and self.isInstalled(arg) :
                self.doInitContacts(arg)
                self.state = 'CONTACTS'
            elif event == 'init-local-done' and not self.isInstalled(arg) and self.isGUIPossible(arg) :
                self.doShowGUI(arg)
                installer.A('init')
                self.doUpdate(arg)
                shutdowner.A('ready')
                self.state = 'INSTALL'
            elif event == 'init-local-done' and not self.isInstalled(arg) and not self.isGUIPossible(arg) :
                shutdowner.A('stop')
                self.state = 'STOPPING'
        #---CONTACTS---
        elif self.state is 'CONTACTS':
            if event == 'init-contacts-done' :
                self.doInitConnection(arg)
                network_connector.A('init')
                p2p_connector.A('init') ;
                self.doShowGUI(arg)
                self.doUpdate(arg)
                shutdowner.A('ready')
                self.state = 'CONNECTION'
            elif ( event == 'shutdowner.state' and arg is 'FINISHED' ) :
                self.doDestroyMe(arg)
                self.state = 'EXIT'
        #---CONNECTION---
        elif self.state is 'CONNECTION':
            if ( event == 'shutdowner.state' and arg is 'FINISHED' ) :
                self.doDestroyMe(arg)
                self.state = 'EXIT'
            elif ( event == 'p2p_connector.state' and arg in [ 'CONNECTED' , 'DISCONNECTED' ] ) :
                self.doInitModules(arg)
                self.doUpdate(arg)
                self.state = 'MODULES'
        #---MODULES---
        elif self.state is 'MODULES':
            if event == 'init-modules-done' :
                self.doUpdate(arg)
                self.state = 'READY'
            elif ( event == 'shutdowner.state' and arg is 'FINISHED' ) :
                self.doDestroyMe(arg)
                self.state = 'EXIT'
        #---INSTALL---
        elif self.state is 'INSTALL':
            if not self.flagCmdLine and ( event == 'installer.state' and arg is 'DONE' ) :
                self.doInitContacts(arg)
                self.doUpdate(arg)
                self.state = 'CONTACTS'
            elif self.flagCmdLine and ( event == 'installer.state' and arg is 'DONE' ) :
                shutdowner.A('stop')
                self.state = 'STOPPING'
            elif ( event == 'shutdowner.state' and arg is 'FINISHED' ) :
                self.doDestroyMe(arg)
                self.state = 'EXIT'
        #---READY---
        elif self.state is 'READY':
            if ( event == 'shutdowner.state' and arg is 'FINISHED' ) :
                self.doDestroyMe(arg)
                self.state = 'EXIT'
        #---STOPPING---
        elif self.state is 'STOPPING':
            if ( event == 'shutdowner.state' and arg is 'FINISHED' ) :
                self.doUpdate(arg)
                self.doDestroyMe(arg)
                self.state = 'EXIT'
        #---EXIT---
        elif self.state is 'EXIT':
            pass

    def isInstalled(self, arg):
        if self.is_installed is None:
            self.is_installed = dhninit.check_install() 
        return self.is_installed
    
    def isGUIPossible(self, arg):
        if dhnio.Windows():
            return True
        if dhnio.Linux():
            return dhnio.X11_is_running()
        return False

    def doUpdate(self, arg):
        webcontrol.OnUpdateStartingPage()

    def doInitLocal(self, arg):
        maybeDeferred(dhninit.init_local, arg).addCallback(
            lambda x: self.automat('init-local-done'))

    def doInitContacts(self, arg):
        dhninit.init_contacts(
            lambda x: self.automat('init-contacts-done'),
            #lambda x: self.automat('init-contacts-failed'), )
            lambda x: self.automat('init-contacts-done'), )

    def doInitConnection(self, arg):
        dhninit.init_connection()

    def doInitModules(self, arg):
        maybeDeferred(dhninit.init_modules).addCallback(
            lambda x: self.automat('init-modules-done'))

    def doShowGUI(self, arg):
        d = webcontrol.init()
        if dhninit.UImode == 'show' or not self.is_installed: 
            d.addCallback(webcontrol.show)
        webcontrol.ready()

    def doDestroyMe(self, arg):
        global _Initializer
        del _Initializer
        _Initializer = None
        automats.get_automats_by_index().pop(self.index)




