#!/usr/bin/env python
#installer.py
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
    sys.exit('Error initializing twisted.internet.reactor in installer.py')
from twisted.internet.defer import Deferred, maybeDeferred
from twisted.internet.task import LoopingCall


import lib.dhnio as dhnio
import lib.dhnnet as dhnnet
import lib.misc as misc
import lib.nameurl as nameurl
import lib.packetid as packetid
import lib.settings as settings
import lib.contacts as contacts
import lib.transport_control as transport_control
import lib.diskusage as diskusage
from lib.automat import Automat


import initializer
import p2p_connector
import identity_registrator
import identity_restorer
import lib.automats as automats

import dhninit
import dhnupdate
import identitypropagate
import install
import webcontrol


_Installer = None

#------------------------------------------------------------------------------ 

def A(event=None, arg=None):
    global _Installer
    if _Installer is None:
        _Installer = Installer('installer', 'AT_STARTUP', 4)
    if event is not None:
        _Installer.automat(event, arg)
    return _Installer


class Installer(Automat):
    output = {}
    MESSAGE_01 = ('incorrect user name', 'red')
    RECOVER_RESULTS = {
        'remote_identity_not_valid':  ('remote Identity is not valid', 'red'),
        'invalid_identity_source':    ('incorrect source of the Identity file', 'red'),
        'invalid_identity_url':       ('incorrect Identity file location', 'red'),
        'remote_identity_bad_format': ('incorrect format of the Identity file', 'red'),
        'incorrect_key':              ('Private Key is not valid', 'red'),
        'idurl_not_exist':            ('Identity URL address not exist or not reachable at this moment', 'blue'),
        'signing_error':              ('unable to sign the local Identity file', 'red'),
        'signature_not_match':        ('remote Identity and Private Key did not match', 'red'),
        'central_failed':             ('unable to connect to the Central server, try again later', 'blue'),
        'success':                    ('account restored!', 'green'), }

    def getOutput(self, state=None):
        if state is None:
            state = self.state
        return self.output.get(state, {})

    def init(self):
        self.flagCmdLine = False

    def state_changed(self, oldstate, newstate):
        automats.set_global_state('INSTALL ' + newstate)
        initializer.A('installer.state', newstate)

    def A(self, event, arg):
        #---AT_STARTUP---
        if self.state == 'AT_STARTUP':
            if event == 'init':
                self.flagCmdLine = False
                self.state = 'WHAT_TO_DO?'
            elif event == 'register-cmd-line':
                self.flagCmdLine = True
                identity_registrator.A('start', arg)
                self.state = 'REGISTER'
            elif event == 'recover-cmd-line':
                self.flagCmdLine = True
                identity_restorer.A('start', arg)
                self.state = 'RECOVER'
        #---WHAT_TO_DO?---
        elif self.state == 'WHAT_TO_DO?':
            if event == 'register-selected':
                self.doUpdate()
                self.state = 'INPUT_NAME'
            elif event == 'recover-selected':
                self.doUpdate()
                self.state = 'LOAD_KEY'
        #---INPUT_NAME---
        elif self.state == 'INPUT_NAME':
            if event == 'back':
                self.doUpdate()
                self.state = 'WHAT_TO_DO?'
            elif event == 'register-start' and self.isNameValid(arg):
                self.doClearOutput()
                identity_registrator.A('start', arg)
                self.doUpdate()
                self.state = 'REGISTER'
            elif event == 'register-start' and not self.isNameValid(arg):
                self.doPrint(self.MESSAGE_01)
                self.doUpdate()
            elif event == 'print':
                self.doPrint(arg)
                self.doUpdate()
        #---LOAD_KEY---
        elif self.state == 'LOAD_KEY':
            if event == 'back':
                self.doUpdate()
                self.state = 'WHAT_TO_DO?'
            elif event == 'load-from-file':
                self.doReadKey(arg)
                self.doUpdate()
            elif event == 'paste-from-clipboard':
                self.doPasteKey()
                self.doUpdate()
            elif event == 'restore-start':
                self.doClearOutput()
                identity_restorer.A('start', arg)
                self.doUpdate()
                self.state = 'RECOVER'
            elif event == 'print':
                self.doPrint(arg)
                self.doUpdate()
        #---REGISTER---
        elif self.state == 'REGISTER':
            if event == 'identity_registrator.state' and arg == 'REGISTERED' and not self.flagCmdLine:
                self.doUpdate()
                self.state = 'AUTHORIZED'
            elif event == 'identity_registrator.state' and arg == 'READY' and not self.flagCmdLine:
                self.doUpdate()
                self.state = 'INPUT_NAME'
            elif event == 'print':
                self.doPrint(arg)
                self.doUpdate()
            elif event == 'identity_registrator.state' and arg in [ 'READY' , 'REGISTERED' ] and self.flagCmdLine:
                self.state = 'DONE'
        #---AUTHORIZED---
        elif self.state == 'AUTHORIZED':
            if event == 'next':
                self.doUpdate()
                self.state = 'CENTRAL'
        #---CENTRAL---
        elif self.state == 'CENTRAL':
            if event == 'central-ready' and self.isCentralValid(arg) and not self.isDirSelected(arg):
                self.doCentralSave(arg)
                self.doUpdate()
                self.state = 'CONTACTS'
            elif event == 'central-ready' and self.isDirSelected(arg):
                self.doDirSave(arg)
                self.doUpdate()
            elif event == 'central-ready' and not self.isCentralValid(arg):
                self.doPrintCentralError(arg)
                self.doUpdate()
        #---CONTACTS---
        elif self.state == 'CONTACTS':
            if event == 'contacts-ready' and self.isContactsValid(arg):
                self.doContactsSave(arg)
                self.doUpdate()
                self.state = 'UPDATES'
            elif event == 'contacts-ready' and not self.isContactsValid(arg):
                self.doPrintContactsError(arg)
                self.doUpdate()
            elif event == 'back':
                self.doUpdate()
                self.state == 'CENTRAL'
        #---UPDATES---
        elif self.state == 'UPDATES':
            if event == 'updates-ready':
                self.doUpdatesSave(arg)
                self.doUpdate()
                self.state = 'DONE'
            elif event == 'back':
                self.doUpdate()
                self.state = 'CONTACTS'
        #---RECOVER---
        elif self.state == 'RECOVER':
            if event == 'identity_restorer.state' and arg == 'DONE' or ( event == 'identity_restorer.state' and arg == 'READY' and self.flagCmdLine ):
                self.doUpdate()
                self.state = 'DONE'
            elif event == 'identity_restorer.state' and arg == 'READY' and not self.flagCmdLine:
                self.state = 'LOAD_KEY'
            elif event == 'print':
                self.doPrint(arg)
                self.doUpdate()
        #---DONE---
        elif self.state == 'DONE':
            pass

    def isNameValid(self, arg):
        if not misc.ValidUserName(arg):
            return False
        return True

    def isDirSelected(self, arg):
        return arg.get('opendir', '') != '' 

    def isCentralValid(self, arg):
        needed = arg.get('needed', '')
        donated = arg.get('donated', '')
        customersdir = arg.get('customersdir', '')
        try:
            neededV = float(needed)
            donatedV = float(donated)
        except:
            return False
        if donatedV < settings.MinimumDonatedMb():
            return False
        if not os.path.isdir(customersdir):
            return False
        if not os.access(customersdir, os.W_OK):
            return False
        freeBytes, totalBytes = diskusage.GetDriveSpace(customersdir)
        if freeBytes <= donatedV * 1024 * 1024:
            return False
        return True

    def isContactsValid(self, arg):
        email = arg.get('email', '').strip()
        phone = arg.get('phone', '')
        fax = arg.get('fax', '')
        text = arg.get('text', '')
        if email == '':
            return False
        if not misc.ValidEmail(email):
            return False
        if phone != '' and not misc.ValidPhone(phone):
            return False
        if fax != '' and not misc.ValidPhone(fax):
            return False
        if len(text) > 500:
            return False
        return True

    def isRecoverSuccess(self, arg):
        return arg == 'success'

    def doClearOutput(self):
        for state in self.output.keys():
            self.output[state] = {'data': [('', 'black')]}

    def doPrint(self, arg):
        text, color = arg
        if not self.output.has_key(self.state):
            self.output[self.state] = {'data': [('', 'black')]}
        self.output[self.state]['data'].append((text, color))
        dhnio.Dprint(0, '  [%s]' % text)

    def doUpdate(self):
        webcontrol.OnUpdateInstallPage()

    def doPrintCentralError(self, arg):
        needed = arg.get('needed', '')
        donated = arg.get('donated', '')
        customersdir = arg.get('customersdir', '')
        try:
            neededV = float(needed)
        except:
            self.doPrint(('incorrect needed space value', 'red'))
            return 
        try:
            donatedV = float(donated)
        except:
            self.doPrint(('incorrect donated space value', 'red'))
            return
        if donatedV < settings.MinimumDonatedMb():
            self.doPrint(('you must donate at least %d MB' % settings.MinimumDonatedMb(), 'blue'))
            return 
        if not os.path.isdir(customersdir):
            self.doPrint(('directory %s not exist' % customersdir, 'red'))
            return 
        if not os.access(customersdir, os.W_OK):
            self.doPrint(('specified folder does not have write permissions', 'red'))
            return 
        freeBytes, totalBytes = diskusage.GetDriveSpace(customersdir)
        if freeBytes <= donatedV * 1024 * 1024:
            self.doPrint(('you do not have enough free space on the hard disk', 'red'))
            return 

    def doCentralSave(self, arg):
        needed = arg.get('needed', '')
        donated = arg.get('donated', '')
        customersdir = arg.get('customersdir', '')
        settings.uconfig().set('central-settings.needed-megabytes', needed+'MB')
        settings.uconfig().set('central-settings.shared-megabytes', donated+'MB')
        settings.uconfig().set('folder.folder-customers', customersdir)
        settings.uconfig().update()

    def doDirSave(self, arg):
        settings.uconfig().set('folder.folder-customers', arg['customersdir'])
        settings.uconfig().update()

    def doPrintContactsError(self, arg):
        email = arg.get('email', '').strip()
        phone = arg.get('phone', '')
        fax = arg.get('fax', '')
        text = arg.get('text', '')
        if email == '':
            self.doPrint(('''<div align=left>
Please enter your e-mail address. 
DataHaven.NET guarantee no spam!
Your e-mail will not be published!. 
We only need to notify you
in case of critical errors
during testing period.</div>
'''.replace('\n', '<br>\n'), 'blue'))
            return 
        if not misc.ValidEmail(email):
            self.doPrint(('incorrect email address', 'red'))
            return 
        if phone != '' and not misc.ValidPhone(phone):
            self.doPrint(('incorrect phone number', 'red'))
            return 
        if fax != '' and not misc.ValidPhone(fax):
            self.doPrint(('incorrect fax number', 'red'))
            return 
        if len(text) > 500:
            self.doPrint(('the text is too long', 'red'))
            return 

    def doContactsSave(self, arg):
        email = arg.get('email', '').strip()
        phone = arg.get('phone', '')
        fax = arg.get('fax', '')
        text = arg.get('text', '')
        settings.uconfig().set('emergency.emergency-email', email)
        settings.uconfig().set('emergency.emergency-phone', phone)
        settings.uconfig().set('emergency.emergency-fax', fax)
        settings.uconfig().set('emergency.emergency-text', text)
        settings.uconfig().update()

    def doUpdatesSave(self, arg):
        shedule = dhnupdate.blank_shedule(arg)
        settings.uconfig().set('updates.updates-shedule', dhnupdate.shedule_to_string(shedule))
        settings.uconfig().update()
    
    def doReadKey(self, arg):
        dhnio.Dprint(2, 'installer.doReadKey arg=[%s]' % str(arg))
        src = dhnio.ReadBinaryFile(arg)
        if len(src) > 1024*10:
            self.doPrint(('file is too big for private key', 'red'))
            return
        try:
            lines = src.split('\n')
            idurl = lines[0]
            txt = '\n'.join(lines[1:])
            if idurl != nameurl.FilenameUrl(nameurl.UrlFilename(idurl)):
                idurl = ''
                txt = src
        except:
            dhnio.DprintException()
            idurl = ''
            txt = src
        if not self.output.has_key(self.state):
            self.output[self.state] = {'data': [('', 'black')]}
        self.output[self.state]['idurl'] = idurl
        self.output[self.state]['keysrc'] = txt
        
    def doPasteKey(self):
        src = misc.getClipboardText()
        try:
            lines = src.split('\n')
            idurl = lines[0]
            txt = '\n'.join(lines[1:])
            if idurl != nameurl.FilenameUrl(nameurl.UrlFilename(idurl)):
                idurl = ''
                txt = src
        except:
            dhnio.DprintException()
            idurl = ''
            txt = src
        if not self.output.has_key(self.state):
            self.output[self.state] = {'data': [('', 'black')]}
        self.output[self.state]['idurl'] = idurl
        self.output[self.state]['keysrc'] = txt

