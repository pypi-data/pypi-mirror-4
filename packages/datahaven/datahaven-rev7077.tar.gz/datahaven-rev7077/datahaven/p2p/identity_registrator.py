#!/usr/bin/env python
#identity_registrator.py
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2012
#    Use of this software constitutes acceptance of the Terms of Use
#      http://datahaven.net/terms_of_use.html
#    All rights reserved.
#
#

import os
import sys
import time

try:
    from twisted.internet import reactor
except:
    sys.exit('Error initializing twisted.internet.reactor in identity_registrator.py')
from twisted.internet.defer import Deferred, DeferredList, maybeDeferred
from twisted.internet.task import LoopingCall


from lib.automat import Automat
import lib.dhnio as dhnio
import lib.misc as misc
import lib.nameurl as nameurl
import lib.settings as settings
import lib.identitycache as identitycache
import lib.stun as stun
import lib.identity as identity
import lib.dhncrypto as dhncrypto
import lib.tmpfile as tmpfile
import lib.dhnnet as dhnnet
import lib.transport_control as transport_control
import lib.transport_tcp as transport_tcp


import installer
import p2p_connector
import lib.automats as automats

import dhninit
import identitypropagate
import webcontrol

_IdentityRegistrator = None
_NewIdentity = None

#------------------------------------------------------------------------------ 

def A(event=None, arg=None):
    global _IdentityRegistrator
    if _IdentityRegistrator is None:
        _IdentityRegistrator = IdentityRegistrator('identity_registrator', 'READY', 4)
    if event is not None:
        _IdentityRegistrator.automat(event, arg)
    return _IdentityRegistrator


class IdentityRegistrator(Automat):
    timers = {'timer-30sec': (30, ['REQUEST_MY_ID']),}
    MESSAGES = {
        'MSG_01': ['checking account name'],
        'MSG_02': ['user %(login)s already exist', 'red'],
        'MSG_03': ['checking network configuration'],
        'MSG_04': ['local IP is %(localip)s'],
        'MSG_05': ['network connection failed', 'red'],
        'MSG_06': ['external IP is %(externalip)s'],
        'MSG_07': ['network connection error', 'red'],
        'MSG_08': ['sending my identity to the identity server'],
        'MSG_09': ['connection error while sending my identity', 'red'],
        'MSG_10': ['verifying my identity on the server'],
        'MSG_11': ['time out connection to the identity server', 'red'],
        'MSG_12': ['verifying my identity'],
        'MSG_13': ['identity verification failed', 'red'],
        'MSG_14': ['new user %(login)s registered successfully!', 'green'], 
        'MSG_15': ['connecting to the identity server'], 
        'MSG_16': ['connection to the identity server was failed', 'red'], }

    def msg(self, arg): 
        msg = self.MESSAGES.get(arg, ['', 'black'])
        text = msg[0] % {
            'login': dhnio.ReadTextFile(settings.UserNameFilename()),
            'externalip': dhnio.ReadTextFile(settings.ExternalIPFilename()),
            'localip': dhnio.ReadTextFile(settings.LocalIPFilename()),}
        color = 'black'
        if len(msg) == 2:
            color = msg[1]
        return text, color

    def state_changed(self, oldstate, newstate):
        automats.set_global_state('ID_REGISTER ' + newstate)
        installer.A('identity_registrator.state', newstate)

    def A(self, event, arg):
        #---READY---
        if self.state == 'READY':
            if event == 'start':
                installer.A('print', self.msg('MSG_15'))
                self.doSaveMyName(arg)
                self.doPingIdentityServer()
                self.state = 'ID_SERVER'
        #---ID_SERVER---
        elif self.state == 'ID_SERVER':
            if event == 'id-server-response':
                installer.A('print', self.msg('MSG_01'))
                self.doRequestMyIdentity()
                self.state = 'USER_NAME'
            elif event == 'id-server-failed':
                installer.A('print', self.msg('MSG_16'))
                self.state = 'READY'
        #---USER_NAME---
        elif self.state == 'USER_NAME':
            if event == 'my-id-exist':
                installer.A('print', self.msg('MSG_02'))
                self.state = 'READY'
            elif event == 'my-id-not-exist':
                installer.A('print', self.msg('MSG_03'))
                self.doDetectLocalIP()
                self.state = 'LOCAL_IP'
        #---LOCAL_IP---
        elif self.state == 'LOCAL_IP':
            if event == 'local-ip-detected':
                installer.A('print', self.msg('MSG_04'))
                self.doStunExternalIP()
                self.state = 'EXTERNAL_IP'
        #---EXTERNAL_IP---
        elif self.state == 'EXTERNAL_IP':
            if event == 'stun-success':
                installer.A('print', self.msg('MSG_06'))
                self.doRequestCentralIdentity()
                self.state = 'CENTRAL_ID'
            elif event == 'stun-failed':
                installer.A('print', self.msg('MSG_05'))
                self.state = 'READY' 
        #---CENTRAL_ID---
        elif self.state == 'CENTRAL_ID':
            if event == 'central-id-success':
                installer.A('print', self.msg('MSG_08'))
                self.doCreateMyIdentity()
                self.doSendMyIdentity()
                self.state = 'SEND_MY_ID'
            elif event == 'central-id-failed':
                installer.A('print', self.msg('MSG_07'))
                self.state = 'READY' 
        #---SEND_MY_ID---
        elif self.state == 'SEND_MY_ID':
            if event == 'my-id-sent':
                installer.A('print', self.msg('MSG_10'))
                self.doRequestMyIdentity()
                self.state = 'REQUEST_MY_ID'
            elif event == 'my-id-failed':
                installer.A('print', self.msg('MSG_09'))
                self.state = 'READY' 
        #---REQUEST_MY_ID---
        elif self.state == 'REQUEST_MY_ID':
            if event == 'my-id-exist' and self.isMyIdentityValid(arg):
                self.doSaveMyIdentity()
                installer.A('print', self.msg('MSG_14'))
                self.state = 'REGISTERED'
            elif event == 'my-id-exist' and not self.isMyIdentityValid(arg):
                installer.A('print', self.msg('MSG_13'))
                self.state = 'READY' 
            elif event == 'my-id-not-exist':
                self.doWait5sec().addCallback(
                    lambda x: self.doRequestMyIdentity())
            elif event == 'timer-30sec':
                installer.A('print', self.msg('MSG_11'))
        #---REGISTERED---
        elif self.state == 'REGISTERED':
            pass
        
    def isMyIdentityValid(self, arg):
        global _NewIdentity
        return _NewIdentity.serialize() == arg

    def doSaveMyName(self, arg):
        login = arg
        dhnio.WriteFile(settings.UserNameFilename(), login)
        webcontrol.installing_process_str = ''

    def doPingIdentityServer(self):
        server_url = nameurl.UrlMake('http', settings.IdentityServerName())
        dhnnet.getPageTwisted(server_url).addCallbacks(
            lambda src: self.automat('id-server-response', src),
            lambda err: self.automat('id-server-failed', err))

    def doRequestMyIdentity(self):
        login = dhnio.ReadTextFile(settings.UserNameFilename())
        idurl = nameurl.UrlMake('http', settings.IdentityServerName(), '', login+'.xml')
        dhnio.Dprint(4, 'identity_registrator.doRequestMyIdentity login=%s, idurl=%s' % (login, idurl))
        dhnnet.getPageTwisted(idurl).addCallbacks(
            lambda src: self.automat('my-id-exist', src),
            lambda err: self.automat('my-id-not-exist', err))
        
    def doDetectLocalIP(self):
        localip = dhnnet.getLocalIp()
        dhnio.WriteFile(settings.LocalIPFilename(), localip)
        dhnio.Dprint(4, 'identity_registrator.doDetectLocalIP [%s]' % localip)
        self.automat('local-ip-detected')
        
    def doStunExternalIP(self):
        dhnio.Dprint(4, 'identity_registrator.doStunExternalIP')
        def save(ip):
            dhnio.Dprint(4, 'identity_registrator.doStunExternalIP.save [%s]' % ip)
            dhnio.WriteFile(settings.ExternalIPFilename(), ip)
            self.automat('stun-success', ip)
        stun.stunExternalIP(close_listener=False, internal_port=settings.getUDPPort()).addCallbacks(
            save, lambda x: self.automat('stun-failed'))

    def doRequestCentralIdentity(self):
        identitycache.immediatelyCaching(settings.CentralID()).addCallbacks(
            lambda x: self.automat('central-id-success'),
            lambda x: self.automat('central-id-failed'))
        
    def doCreateMyIdentity(self):
        CreateNewIdentity()
        
    def doSendMyIdentity(self):
        dl = SendNewIdentity()
        dl.addCallback(lambda x: self.automat('my-id-sent'))
        dl.addErrback(lambda x: self.automat('my-id-failed'))
        
    def doSaveMyIdentity(self):
        global _NewIdentity
        misc.setLocalIdentity(_NewIdentity)
        misc.saveLocalIdentity()
        
    def doWait5sec(self):
        d = Deferred()
        reactor.callLater(5, d.callback, 0)
        return d
        
def CreateNewIdentity():
    global _NewIdentity
    
    misc.loadLocalIdentity()
    if misc.isLocalIdentityReady():
        if misc.getLocalIdentity().Valid():
            _NewIdentity = misc.getLocalIdentity()
            return
        else:
            dhnio.Dprint(2, 'identity_registrator.CreateNewIdentity ERROR local identity is not VALID!!!')

    login = dhnio.ReadTextFile(settings.UserNameFilename())
    externalIP = dhnio.ReadTextFile(settings.ExternalIPFilename())
    localIP = dhnio.ReadTextFile(settings.LocalIPFilename())

    dhnio.Dprint(4, 'identity_registrator.CreateNewIdentity %s %s ' % (login, externalIP))
    
    idurl = 'http://'+settings.DefaultIdentityServer()+'/'+login.lower()+'.xml'
    ident = identity.identity( )
    ident.sources.append(idurl)

    cdict = {}
    if settings.enableTCP():
        cdict['tcp'] = 'tcp://'+externalIP+':'+settings.getTCPPort()
    if settings.enableCSpace() and transport_control._TransportCSpaceEnable:
        cdict['cspace'] = 'cspace://'
        if settings.getCSpaceKeyID() != '':
            cdict['cspace'] += settings.getCSpaceKeyID()
    if settings.enableUDP() and transport_control._TransportUDPEnable:
        if stun.getUDPClient() is not None:
            if stun.getUDPClient().externalAddress is not None: # _altStunAddress
                cdict['udp'] = 'udp://'+stun.getUDPClient().externalAddress[0]+':'+str(stun.getUDPClient().externalAddress[1])
        
    for c in misc.validTransports:
        if cdict.has_key(c):
            ident.contacts.append(cdict[c])

    ident.publickey = dhncrypto.MyPublicKey()
    ident.date = time.ctime() #time.strftime('%b %d, %Y')

    revnum = dhnio.ReadTextFile(settings.RevisionNumberFile()).strip()
    repo, location = misc.ReadRepoLocation()
    ident.version = (revnum.strip() + ' ' + repo.strip() + ' ' + dhnio.osinfo().strip()).strip()

    ident.sign()
    
    dhnio.WriteFile(settings.LocalIdentityFilename()+'.new', ident.serialize())
    
    _NewIdentity = ident
    

def SendNewIdentity():
    global _NewIdentity
    dhnio.Dprint(4, 'identity_registrator.SendNewIdentity ')

    sendfile, sendfilename = tmpfile.make("propagate")
    os.close(sendfile)
    src = _NewIdentity.serialize()
    dhnio.WriteFile(sendfilename, src)

    dlist = []
    for idurl in _NewIdentity.sources:            
        # sources for out identity are servers we need to send to
        protocol, host, port, filename = nameurl.UrlParse(idurl)
        port = settings.IdentityServerPort()
        dlist.append(transport_tcp.send(sendfilename, host, port, False))

    dl = DeferredList(dlist)
    return dl
                
        
        


