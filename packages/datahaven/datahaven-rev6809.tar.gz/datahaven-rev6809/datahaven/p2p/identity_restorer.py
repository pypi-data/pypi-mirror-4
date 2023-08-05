#!/usr/bin/env python
#identity_restorer.py
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2012
#    All rights reserved.
#
#

import os
import sys
import time

try:
    from twisted.internet import reactor
except:
    sys.exit('Error initializing twisted.internet.reactor in identity_restorer.py')
from twisted.internet.defer import Deferred, DeferredList, maybeDeferred
from twisted.internet.task import LoopingCall


from lib.automat import Automat
import lib.dhnio as dhnio
import lib.misc as misc
import lib.settings as settings
import lib.identitycache as identitycache
import lib.identity as identity
import lib.dhncrypto as dhncrypto
import lib.dhnnet as dhnnet


import installer
import lib.automats as automats

import webcontrol

_IdentityRestorer = None
_WorkingIDURL = ''
_WorkingKey = ''

#------------------------------------------------------------------------------ 

def A(event=None, arg=None):
    global _IdentityRestorer
    if _IdentityRestorer is None:
        _IdentityRestorer = IdentityRestorer('identity_restorer', 'READY', 4)
    if event is not None:
        _IdentityRestorer.automat(event, arg)
    return _IdentityRestorer


class IdentityRestorer(Automat):
    MESSAGES = {
        'MSG_01':   ['download central server identity'], 
        'MSG_02':   ['network connection failed', 'red'],
        'MSG_03':   ['download my identity'],
        'MSG_04':   ['identity not exist', 'red'],
        'MSG_05':   ['verifying my identity and private key'],
        'MSG_06':   ['my account were restored? cool!', 'green'], }
    
    def msg(self, arg): 
        msg = self.MESSAGES.get(arg, ['', 'black'])
        text = msg[0]
        color = 'black'
        if len(msg) == 2:
            color = msg[1]
        return text, color
    
    def state_changed(self, oldstate, newstate):
        automats.set_global_state('ID_RESTORE ' + newstate)
        installer.A('identity_restorer.state', newstate)

    def A(self, event, arg):
        #---READY---
        if self.state == 'READY':
            if event == 'start':
                installer.A('print', self.msg('MSG_01'))
                self.doSetWorkingIDURL(arg)
                self.doSetWorkingKey(arg)
                self.doRequestCentralIdentity()
                self.state = 'CENTRAL_ID'
        #---CENTRAL_ID---
        elif self.state == 'CENTRAL_ID':
            if event == 'central-id-failed':
                installer.A('print', self.msg('MSG_02'))
                self.doClearWorkingIDURL()
                self.doClearWorkingKey()
                self.state = 'READY'
            elif event == 'central-id-received':
                installer.A('print', self.msg('MSG_03'))
                self.doRequestMyIdentity()
                self.state = 'MY_ID' 
        #---MY_ID---
        elif self.state == 'MY_ID':
            if event == 'my-id-failed':
                installer.A('print', self.msg('MSG_04'))
                self.doClearWorkingIDURL()
                self.doClearWorkingKey()
                self.state = 'READY'
            elif event == 'my-id-received':
                installer.A('print', self.msg('MSG_05'))
                self.doVerifyAndRestore(arg)
                self.state = 'WORK'                 
        #---WORK---
        elif self.state == 'WORK':
            if event == 'restore-failed':
                installer.A('print', arg)
                self.doClearWorkingIDURL()
                self.doClearWorkingKey()
                self.state = 'READY'
            elif event == 'restore-success':
                installer.A('print', self.msg('MSG_06'))
                self.doRestoreSave()
                self.state = 'DONE' 
        #---DONE---
        elif self.state == 'DONE':
            pass
                
    def doSetWorkingIDURL(self, arg):
        global _WorkingIDURL
        _WorkingIDURL = arg['idurl']
        
    def doSetWorkingKey(self, arg):
        global _WorkingKey
        _WorkingKey = arg['keysrc']

    def doClearWorkingIDURL(self):
        global _WorkingIDURL
        _WorkingIDURL = ''
        
    def doClearWorkingKey(self):
        global _WorkingKey
        _WorkingKey = ''

    def doRequestCentralIdentity(self):
        dhnio.Dprint(4, 'identity_restorer.doRequestCentralIdentity')
        identitycache.immediatelyCaching(settings.CentralID()).addCallbacks(
            lambda x: self.automat('central-id-received'),
            lambda x: self.automat('central-id-failed'))
        
    def doRequestMyIdentity(self):
        global _WorkingIDURL
        idurl = _WorkingIDURL
        dhnio.Dprint(4, 'identity_restorer.doRequestMyIdentity %s' % idurl)
        dhnnet.getPageTwisted(idurl).addCallbacks(
            lambda src: self.automat('my-id-received', src),
            lambda err: self.automat('my-id-failed', err))
    
    def doVerifyAndRestore(self, arg):
        global _WorkingKey
        dhnio.Dprint(4, 'identity_restorer.doVerifyAndRestore')
    
        remote_identity_src = arg

        if os.path.isfile(settings.KeyFileName()):
            dhnio.Dprint(4, 'identity_restorer.doVerifyAndRestore will backup and remove ' + settings.KeyFileName())
            dhnio.backup_and_remove(settings.KeyFileName())

        if os.path.isfile(settings.LocalIdentityFilename()):    
            dhnio.Dprint(4, 'identity_restorer.doVerifyAndRestore will backup and remove ' + settings.LocalIdentityFilename())
            dhnio.backup_and_remove(settings.LocalIdentityFilename())
    
        try:
            remote_ident = identity.identity(xmlsrc = remote_identity_src)
            local_ident = identity.identity(xmlsrc = remote_identity_src)
        except:
            dhnio.DprintException()
            self.automat('restore-failed', 'remote identity have incorrect format' )
            return
    
        try:
            res = remote_ident.Valid()
        except:
            dhnio.DprintException()
            res = False
        if not res:
            self.automat('restore-failed', 'remote_identity_not_valid')
            return
    
        dhncrypto.ForgetMyKey()
        dhnio.WriteFile(settings.KeyFileName(), _WorkingKey)
        try:
            dhncrypto.InitMyKey()
        except:
            dhnio.DprintException()
            try:
                os.remove(settings.KeyFileName())
            except:
                pass
            self.automat('restore-failed', 'private key not valid')
            return
    
        try:
            local_ident.sign()
        except:
            dhnio.DprintException()
            self.automat('restore-failed', 'error while signing identity')
            return
    
        if remote_ident.signature != local_ident.signature:
            self.automat('restore-failed', 'signature do not match')
            return
    
        misc.setLocalIdentity(local_ident)
        misc.saveLocalIdentity()
    
        dhnio.WriteFile(settings.UserNameFilename(), misc.getIDName())
    
        if os.path.isfile(settings.KeyFileName()+'.backup'):
            dhnio.Dprint(4, 'identity_restorer.doVerifyAndRestore will remove backup file for ' + settings.KeyFileName())
            dhnio.remove_backuped_file(settings.KeyFileName())

        if os.path.isfile(settings.LocalIdentityFilename()+'.backup'):
            dhnio.Dprint(4, 'identity_restorer.doVerifyAndRestore will remove backup file for ' + settings.LocalIdentityFilename())
            dhnio.remove_backuped_file(settings.LocalIdentityFilename())

        self.automat('restore-success')
        
    def doRestoreSave(self):
        settings.uconfig().set('central-settings.desired-suppliers', '0')
        settings.uconfig().set('central-settings.needed-megabytes', '0Mb')
        settings.uconfig().set('central-settings.shared-megabytes', '0Mb')
        settings.uconfig().update()






