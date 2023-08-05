#!/usr/bin/env python
#p2p_connector.py
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
    sys.exit('Error initializing twisted.internet.reactor in p2p_connector.py')
from twisted.internet.defer import Deferred, DeferredList, maybeDeferred, succeed
from twisted.internet.task import LoopingCall


import lib.dhnio as dhnio
import lib.misc as misc
import lib.nameurl as nameurl
import lib.settings as settings
import lib.stun as stun
import lib.transport_control as transport_control
import lib.transport_tcp as transport_tcp
if transport_control._TransportCSpaceEnable:
    import lib.transport_cspace as transport_cspace
if transport_control._TransportUDPEnable:
    import lib.transport_udp as transport_udp


import lib.automat as automat
import lib.automats as automats

import initializer
import shutdowner
import central_connector
import backup_monitor
import network_connector

import identitypropagate
import run_upnpc
import ratings
import dhnicon


_P2PConnector = None
_RevisionNumber = None
_WorkingProtocols = set()

#------------------------------------------------------------------------------

def A(event=None, arg=None):
    global _P2PConnector
    if _P2PConnector is None:
        _P2PConnector = P2PConnector('p2p_connector', 'AT_STARTUP', 6)
    if event is not None:
        _P2PConnector.automat(event, arg)
    return _P2PConnector

class P2PConnector(automat.Automat):
    timers = {'timer-1min':  (60, ['INCOMMING?', 'DISCONNECTED']),
              'timer-20sec': (20, ['INCOMMING?']),}

    def init(self):
        self.ackCounter = 0

    def state_changed(self, oldstate, newstate):
        automats.set_global_state('P2P ' + newstate)
        initializer.A('p2p_connector.state', newstate)
        central_connector.A('p2p_connector.state', newstate)
        if newstate in ['CONNECTED']:
            dhnicon.set('green')
        elif newstate in ['DISCONNECTED']:
            dhnicon.set('gray')
        else:
            dhnicon.set('gray')

    def A(self, event, arg):
        #---AT_STARTUP---
        if self.state == 'AT_STARTUP':
            if event == 'init':
                self.doInit()
                self.state = 'NETWORK?'
        #---NETWORK?---
        elif self.state == 'NETWORK?':
            if event == 'network_connector.state' and arg in ['CONNECTED', 'DISCONNECTED']:
                self.doUpdateIdentity()
                self.doUpdateTransports(arg)
                self.state = 'TRANSPORTS'
        #---TRANSPORTS---
        elif self.state == 'TRANSPORTS':
            if event == 'transports-updated':
                self.doUpdateIdentity()
                self.doSendIdentityToIDServer()
                self.state = 'ID_SERVER'
        #---ID_SERVER---
        elif self.state == 'ID_SERVER':
            if event in ['id-server-success', 'id-server-failed']:
                central_connector.A('propagate')
                if transport_control._TransportUDPEnable and settings.enableUDP():
                    transport_udp.A('start')
                self.state = 'CENTRAL_SERVER'
        #---CENTRAL_SERVER---
        elif self.state == 'CENTRAL_SERVER':
            if event == 'central_connector.state' and arg in ['CONNECTED', 'DISCONNECTED']:
                self.doSendIdentityToAllContacts()
                self.state = 'CONTACTS'
            elif event == 'central_connector.state' and arg is 'ONLY_ID':
                self.doUpdateIdentity()
                self.doPopBestProto()
                self.doUpdateTransports(arg)
                self.state = 'TRANSPORTS'
        #---CONTACTS---
        elif self.state == 'CONTACTS':
            if event == 'identity-sent-to-all':
                self.state = 'INCOMMING?'
            elif event == 'settings' and self.isIdentityChanged(arg):
                self.doUpdateIdentity()
                self.doUpdateTransports(arg)
                self.state = 'TRANSPORTS'
        #---INCOMMING?---
        elif self.state == 'INCOMMING?':
            #if event == 'timer-20sec' and self.isAnyInboxPackets():
            if event == 'inbox-packet' and self.isUsingBestProto():
                self.doInitRatings()
                backup_monitor.A('restart')
                self.state = 'CONNECTED'
            elif event == 'inbox-packet' and not self.isUsingBestProto():
                self.doUpdateIdentity()
                self.doPopBestProto()
                self.doUpdateTransports(arg)
                self.state = 'TRANSPORTS'
            elif event == 'settings' and self.isIdentityChanged(arg):
                self.doUpdateIdentity()
                self.doUpdateTransports(arg)
                self.state = 'TRANSPORTS'
            elif event == 'timer-1min':
                self.doInitRatings()
                self.state = 'DISCONNECTED'
        #---CONNECTED---
        elif self.state == 'CONNECTED':
            if event == 'settings' and self.isIdentityChanged(arg):
                self.doUpdateIdentity()
                self.doUpdateTransports(arg)
                self.state = 'TRANSPORTS'
            elif event == 'network_connector.state' and arg is 'DISCONNECTED':
                self.state = 'DISCONNECTED'
            elif event == 'network_connector.state' and arg not in ['CONNECTED', 'DISCONNECTED']:
                self.state = 'NETWORK?'
        #---DISCONNECTED---
        elif self.state == 'DISCONNECTED':
            if event == 'inbox-packet' or ( event == 'settings' and self.isIdentityChanged(arg) ) or ( event == 'network_connector.state' and arg is 'CONNECTED' ) or ( event == 'timer-1min' and self.isNetworkConnected() ):
                self.doUpdateIdentity()
                self.doUpdateTransports(arg)
                self.state = 'TRANSPORTS'
            elif event == 'network_connector.state' and arg not in ['CONNECTED', 'DISCONNECTED']:
                self.state = 'NETWORK?'

    def isUsingBestProto(self):
        return DoWeUseTheBestProto()

    def isIdentityChanged(self, arg):
        return IDchanged(arg)

    def isAnyInboxPackets(self):
        return self.ackCounter > 0
    
    def isNetworkConnected(self):
        return network_connector.A().state == 'CONNECTED'

    def doInit(self):
        global _RevisionNumber
        _RevisionNumber = dhnio.ReadTextFile(settings.RevisionNumberFile()).strip()
        transport_control.AddInboxCallback(Inbox)

    def doCheckPacketProto(self, arg):
        global _WorkingProtocols
        _WorkingProtocols.add(arg[1])

    def doUpdateIdentity(self):
        UpdateIdentity()

    def doUpdateTransports(self, arg):
        UpdateTransports(arg)

    def doSendIdentityToIDServer(self):
        identitypropagate.update().addCallbacks(
            lambda x: self.automat('id-server-success'),
            lambda x: self.automat('id-server-failed'), )
        
    def doSendIdentityToAllContacts(self):
        self.ackCounter = 0
        def increaseAckCounter(packet):
            self.ackCounter += 1
        identitypropagate.start(
            increaseAckCounter).addBoth(
                lambda x: self.automat('identity-sent-to-all'))

    def doPopBestProto(self):
        PopWorkingProto()

    def doInitRatings(self):
        ratings.init()

#-------------------------------------------------------------------------------

def Inbox(newpacket, proto, host, status=None, message=None):
    global _WorkingProtocols
    if proto not in _WorkingProtocols:
        dhnio.Dprint(2, 'p2p_connector.Inbox [transport_%s] seems to work !!!!!!!!!!!!!!!!!!!!!' % proto)
        dhnio.Dprint(2, '                    We got the first packet from %s://%s' % (proto, host))
    _WorkingProtocols.add(proto)
    A('inbox-packet', (newpacket, proto, host, status, message))


def IPisLocal():
    externalip = misc.readExternalIP()
    localip = misc.readLocalIP()
    return localip != externalip


#if some transports was enabled or disabled we want to update identity contacts
#we empty all of the contacts and create it again in the same order
def UpdateIdentity():
    global _RevisionNumber
    global _WorkingProtocols

    #getting local identity
    lid = misc.getLocalIdentity()
    nowip = misc.readExternalIP()
    order = lid.getProtoOrder()
    lid.clearContacts()

    #prepare contacts data
    cdict = {}
    cdict['tcp'] = 'tcp://'+nowip+':'+settings.getTCPPort()
    if transport_control._TransportSSHEnable:
        cdict['ssh'] = 'ssh://'+nowip+':'+settings.getSSHPort()
    if transport_control._TransportHTTPEnable:
        cdict['http'] = 'http://'+nowip+':'+settings.getHTTPPort()
    if transport_control._TransportQ2QEnable:
        cdict['q2q'] = 'q2q://'+settings.getQ2Quserathost()
    if transport_control._TransportEmailEnable:
        cdict['email'] = 'email://'+settings.getEmailAddress()
    if transport_control._TransportCSpaceEnable:
        cdict['cspace'] = 'cspace://'+settings.getCSpaceKeyID()
    if transport_control._TransportUDPEnable:
        if stun.getUDPClient() is None or stun.getUDPClient().externalAddress is None:
            cdict['udp'] = 'udp://'+nowip+':'+settings.getUDPPort()
        else:
            cdict['udp'] = 'udp://'+stun.getUDPClient().externalAddress[0]+':'+str(stun.getUDPClient().externalAddress[1])

    #making full order list
    for proto in cdict.keys():
        if proto not in order:
            order.append(proto)

    #add contacts data to the local identity
    #check if some transport is not installed
    for proto in order:
        if settings.transportIsEnabled(proto):
            contact = cdict.get(proto, None)
            if contact is not None:
                lid.setProtoContact(proto, contact)
        else:
            # if protocol is disabled - mark this
            # because we may want to turn it on in the future
            _WorkingProtocols.discard(proto)
            
    #misc.setLocalIdentity(lid)

    del order

#    #if IP is not external and upnp configuration was failed for some reasons
#    #we want to use another contact methods, NOT tcp or ssh
#    if IPisLocal() and run_upnpc.last_result('tcp') != 'upnp-done':
#        dhnio.Dprint(4, 'p2p_connector.update_identity want to push tcp contact: local IP, no upnp ...')
#        lid.pushProtoContact('tcp')
#        misc.setLocalIdentity(lid)

    #update software version number
    revnum = _RevisionNumber.strip()
    repo, location = misc.ReadRepoLocation()
    lid.version = (revnum.strip() + ' ' + repo.strip() + ' ' + dhnio.osinfo().strip()).strip()
    
    #generate signature with changed content
    lid.sign()
    
    #remember the identity
    misc.setLocalIdentity(lid)

    #finally saving local identity
    misc.saveLocalIdentity()
    dhnio.Dprint(4, 'p2p_connector.UpdateIdentity %s' % str(lid.contacts))
    #_UpnpResult.clear()


def UpdateTransports(arg):
    dhnio.Dprint(4, 'p2p_connector.UpdateTransports')
    changes = set()
    if arg:
        changes = set(arg)
    # let's stop transport not needed anymore
    # also need to stop transport if its options was changed
    def _stop_transports():
        stoplist = []
        for proto in transport_control.ListSupportedProtocols():
            contact = misc.getLocalIdentity().getProtoContact(proto)
            if contact is None:
                dhnio.Dprint(4, 'p2p_connector.UpdateTransports want to stop transport %s because not present in local identity' % proto)
                stoplist.append(transport_control.StopProtocol(proto))
                continue
            proto_, host, port, filename = nameurl.UrlParse(contact)
            if host.strip() == '':
                continue
            opts = transport_control.ProtocolOptions(proto)
            if opts[0].strip() == '':
                continue
            if proto != proto_:
                dhnio.Dprint(8, 'p2p_connector.UpdateTransports WARNING identity contact is %s, but proto is %s' % (contact, proto))
                continue
            #---tcp---
            if proto == 'tcp':
                if opts[0] != host:
                    dhnio.Dprint(4, 'p2p_connector.UpdateTransports want to stop transport [tcp] because IP changed')
                    stoplist.append(transport_control.StopProtocol(proto))
                    continue
                if opts[1] != port:
                    dhnio.Dprint(4, 'p2p_connector.UpdateTransports want to stop transport [tcp] because port changed')
                    stoplist.append(transport_control.StopProtocol(proto))
                    continue
            #---cspace---
            if proto == 'cspace':
                if opts[0] != host:
                    dhnio.Dprint(4, 'p2p_connector.UpdateTransports want to stop transport [cspace] because keyID changed: %s to %s' % (
                        host, opts[0]))
                    stoplist.append(transport_control.StopProtocol(proto))
                    continue
            #---udp---
            if proto == 'udp':
                if opts[0] != host:
                    dhnio.Dprint(4, 'p2p_connector.UpdateTransports want to stop transport [udp] because IP were changed')
                    stoplist.append(transport_control.StopProtocol(proto))
                    continue
                if opts[1] != port:
                    dhnio.Dprint(4, 'p2p_connector.UpdateTransports want to stop transport [udp] because port were changed')
                    stoplist.append(transport_control.StopProtocol(proto))
                    continue
                if 'transport.transport-udp.transport-udp-port' in changes and settings.enableUDP():
                    dhnio.Dprint(4, 'p2p_connector.UpdateTransports want to stop transport [udp] because port were changed by user')
                    stoplist.append(transport_control.StopProtocol(proto))
                    continue
        #need to wait before all listeners will be stopped
        return DeferredList(stoplist)

    # let's start transport that isn't started yet
    def _start_transports():
        startlist = []
        for contact in misc.getLocalIdentity().getContacts():
            proto, host, port, filename = nameurl.UrlParse(contact)
            opts = transport_control.ProtocolOptions(proto)
            if not transport_control.ProtocolIsSupported(proto):
                if settings.transportIsEnabled(proto) and settings.transportIsInstalled(proto):
                    #---tcp---
                    if proto == 'tcp':
                        def _tcp_started(l, opts):
                            dhnio.Dprint(4, 'p2p_connector.UpdateTransports._tcp_started')
                            if l is not None:
                                transport_control.StartProtocol('tcp', l, opts[0], opts[1], opts[2])
                        def _tcp_failed(x):
                            dhnio.Dprint(4, 'p2p_connector.UpdateTransports._tcp_failed WARNING: '+str(x))
                        def _start_tcp(options):
                            dhnio.Dprint(4, 'p2p_connector.UpdateTransports._start_tcp on port %d' % int(options[1]))
                            d = transport_tcp.receive(int(options[1]))
                            d.addCallback(_tcp_started, options)
                            d.addErrback(_tcp_failed)
                            startlist.append(d)
                        def _upnp_result(result, options):
                            dhnio.Dprint(4, 'p2p_connector.UpdateTransports._upnp_result %s' % str(result))
                            #if result[1] != int(options[1]):
                            if result is not None:
                                options[1] = str(result[1])
                            _start_tcp(options)
                        def _run_upnpc(port):
                            shutdowner.A('block')
                            run_upnpc.update(port)
                            shutdowner.A('unblock')
                        externalIP = misc.readExternalIP() 
                        if opts is None:
                            opts = (externalIP, '', '')
                        opts = list(opts)
                        opts[0] = externalIP
                        opts[1] = settings.getTCPPort()
                        if settings.enableUPNP():
                            d = maybeDeferred(_run_upnpc, int(opts[1]))
                            d.addCallback(_upnp_result, opts)
                        else:
                            _start_tcp(opts)
                        del opts
                    #---cspace---
                    elif proto == 'cspace' and transport_control._TransportCSpaceEnable:
                        def _cspace_started(x, opts):
                            dhnio.Dprint(4, 'p2p_connector.UpdateTransports._cspace_started')
                            l = transport_cspace.getListener()
                            if l is not None:
                                transport_control.StartProtocol('cspace', l, opts[0], opts[1], opts[2])
                        def _cspace_failed(x):
                            dhnio.Dprint(4, 'p2p_connector.UpdateTransports._cspace_failed WARNING: ' + str(x))
                        if opts is None:
                            opts = (settings.getCSpaceKeyID(), '', '')
                        opts = list(opts)
                        opts[0] = settings.getCSpaceKeyID()
                        if transport_cspace.my_state() == '':
                            d = transport_cspace.init()
                        else:
                            d = maybeDeferred(transport_cspace.go_online)
                        d.addCallback(_cspace_started, opts)
                        d.addErrback(_cspace_failed)
                        startlist.append(d)
                        del opts
                    #---udp---
                    elif proto == 'udp' and transport_control._TransportUDPEnable:
                        def _udp_start(x, opts):
                            dhnio.Dprint(4, 'p2p_connector.UpdateTransports._udp_start')
                            if opts is None:
                                opts = (stun.getUDPClient().externalAddress[0], str(stun.getUDPClient().externalAddress[1]), '')
                            opts = list(opts)
                            opts[0] = stun.getUDPClient().externalAddress[0]
                            opts[1] = str(stun.getUDPClient().externalAddress[1])
                            transport_udp.init(stun.getUDPClient())
                            l = transport_udp.getListener()
                            if l is not None:
                                transport_control.StartProtocol('udp', l, opts[0], opts[1], opts[2])
                            del opts
                        def _udp_failed(x):
                            dhnio.Dprint(4, 'p2p_connector.UpdateTransports._udp_failed')
                        if stun.getUDPClient() is None or stun.getUDPClient().externalAddress is None:
                            d = stun.stunExternalIP(close_listener=False, internal_port=settings.getUDPPort())
                        else:
                            d = succeed('')
                        d.addCallback(_udp_start, opts)
                        d.addCallback(_udp_failed)
                        startlist.append(d)
                        
        #need to wait before all listeners will be started
        return DeferredList(startlist)

    transport_control.init(
        lambda: _stop_transports().addBoth(
            lambda x: _start_transports().addBoth(
                lambda x: A('transports-updated'))))


def IDchanged(changes):
    s = set(changes)
    if s.intersection([
        'transport.transport-tcp.transport-tcp-enable',
        'transport.transport-udp.transport-udp-enable',
        'transport.transport-ssh.transport-ssh-enable',
        'transport.transport-http.transport-http-enable',
        'transport.transport-email.transport-email-enable',
        'transport.transport-q2q.transport-q2q-enable',
        'transport.transport-cspace.transport-cspace-enable',
        'transport.transport-skype.transport-skype-enable',
        ]):
        return True
    if 'transport.transport-tcp.transport-tcp-port' in s and settings.enableTCP():
        return True
    if 'transport.transport-udp.transport-udp-port' in s and settings.enableUDP():
        return True
    if 'transport.transport-ssh.transport-ssh-port' in s and settings.enableSSH():
        return True
    if 'transport.transport-q2q.transport-q2q-username' in s and settings.enableQ2Q():
        return True
    if 'transport.transport-cspace.transport-cspace-key-id' in s and settings.enableCSpace():
        return True
    if 'transport.transport-http.transport-http-server-port' in s and settings.enableHTTP():
        return True
    if 'transport.transport-tcp.transport-tcp-port' in s and settings.enableTCP():
        return True
    return False

#    global _SettingsChanges
#    if _SettingsChanges.intersection([
#        'transport.transport-tcp.transport-tcp-enable',
#        'transport.transport-ssh.transport-ssh-enable',
#        'transport.transport-http.transport-http-enable',
#        'transport.transport-email.transport-email-enable',
#        'transport.transport-q2q.transport-q2q-enable',
#        'transport.transport-cspace.transport-cspace-enable',
#        'transport.transport-skype.transport-skype-enable',
#        ]):
#        return True
#    if 'transport.transport-tcp.transport-tcp-port' in _SettingsChanges and settings.enableTCP():
#        return True
#    if 'transport.transport-ssh.transport-ssh-port' in _SettingsChanges and settings.enableSSH():
#        return True
#    if 'transport.transport-q2q.transport-q2q-username' in _SettingsChanges and settings.enableQ2Q():
#        return True
#    if 'transport.transport-http.transport-http-server-port' in _SettingsChanges and settings.enableHTTP():
#        return True
#    if 'transport.transport-tcp.transport-tcp-port' in _SettingsChanges and settings.enableTCP():
#        return True
#    if 'transport.transport-cspace.transport-cspace-key-id' in _SettingsChanges and settings.enableCSpace():
#        return True
#    return False


def DoWeUseTheBestProto():
    global _WorkingProtocols
    #dhnio.Dprint(4, 'p2p_connector.DoWeUseTheBestProto _WorkingProtocols=%s' % str(_WorkingProtocols))
    #if no incomming traffic - do nothing
    if len(_WorkingProtocols) == 0:
        return True
    lid = misc.getLocalIdentity()
    order = lid.getProtoOrder()
    #if no protocols in local identity - do nothing
    if len(order) == 0:
        return True
    first = order[0]
    #if first contact in local identity is not working yet
    #but there is another working methods - switch first method
    if first not in _WorkingProtocols:
        dhnio.Dprint(2, 'p2p_connector.DoWeUseTheBestProto first contact (%s) is not working!   _WorkingProtocols=%s' % (first, str(_WorkingProtocols)))
        return False
    #if tcp contact is on first place and it is working - we are VERY HAPPY! - no need to change anything - return False
    if first == 'tcp' and 'tcp' in _WorkingProtocols:
        return True
    #but if tcp method is not the first ant it works - we want to TURN IT ON! - return True
    if first != 'tcp' and 'tcp' in _WorkingProtocols:
        dhnio.Dprint(2, 'p2p_connector.DoWeUseTheBestProto tcp is not first but it works _WorkingProtocols=%s' % str(_WorkingProtocols))
        return False
    #next good solution is q2q, it should be faster than http.
    #we already deal with tcp, if we reach this line - tcp not in the _WorkingProtocols
    #So if q2q method is not the first but it works - switch to q2q
    if first != 'q2q' and 'q2q' in _WorkingProtocols:
        dhnio.Dprint(2, 'p2p_connector.DoWeUseTheBestProto q2q is not first but it works _WorkingProtocols=%s' % str(_WorkingProtocols))
        return False
    #cspace should be better than q2q - but let's check it first
    if first != 'cspace' and 'cspace' in _WorkingProtocols:
        dhnio.Dprint(2, 'p2p_connector.DoWeUseTheBestProto cspace is not first but it works _WorkingProtocols=%s' % str(_WorkingProtocols))
        return False
    #udp is not tested yet - the last solution
    if first != 'udp' and 'udp' in _WorkingProtocols:
        dhnio.Dprint(2, 'p2p_connector.DoWeUseTheBestProto udp is not first but it works _WorkingProtocols=%s' % str(_WorkingProtocols))
        return False
    #in other cases - do nothing
    return True


def PopWorkingProto():
    global _WorkingProtocols
    lid = misc.getLocalIdentity()
    order = lid.getProtoOrder()
    first = order[0]
    wantedproto = ''
    #if first contact in local identity is not working yet
    #but there is another working methods - switch first method
    if first not in _WorkingProtocols:
        #take (but not remove) any item from the set
        wantedproto = _WorkingProtocols.pop()
        _WorkingProtocols.add(wantedproto)
    #if udp method is not the first but it works - switch to udp
    if first != 'udp' and 'udp' in _WorkingProtocols:
        wantedproto = 'udp'
    # if q2q method is not the first but it works - switch to q2q
    # disabled because we do not use q2q now
    # if first != 'q2q' and 'q2q' in _WorkingProtocols:
    #     wantedproto = 'q2q'
    #if cspace method is not the first but it works - switch to cspace
    if first != 'cspace' and 'cspace' in _WorkingProtocols:
        wantedproto = 'cspace'
    #if tcp method is not the first but it works - switch to tcp
    if first != 'tcp' and 'tcp' in _WorkingProtocols:
        wantedproto = 'tcp'
    dhnio.Dprint(4, 'p2p_connector.pop_working_proto will pop %s contact   order=%s _WorkingProtocols=%s' % (wantedproto, str(order), str(_WorkingProtocols)))
    # now move best proto on the top
    # other users will use this method to send to us
    lid.popProtoContact(wantedproto)
    # save local id
    # also need to propagate our identity
    # other users must know our new contacts
    misc.setLocalIdentity(lid)
    misc.saveLocalIdentity()

#------------------------------------------------------------------------------ 

def shutdown():
    dhnio.Dprint(4, 'p2p_connector.shutdown')
    automat.clear_object(A().index)

