#!/usr/bin/env python
#automats.py
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
    sys.exit('Error initializing twisted.internet.reactor in automat.py')
from twisted.internet.defer import Deferred, maybeDeferred
from twisted.internet.task import LoopingCall
from twisted.internet import threads

from lib.automat import Automat
import lib.automats as automats

import lib.dhnio as dhnio
import lib.misc as misc
import lib.settings as settings
import lib.stun as stun
import lib.dhnnet as dhnnet
import lib.transport_control as transport_control
if transport_control._TransportCSpaceEnable:
    import lib.transport_cspace as transport_cspace

import p2p_connector
import shutdowner
import run_upnpc


_NetworkConnector = None

#------------------------------------------------------------------------------

def A(event=None, arg=None):
    global _NetworkConnector
    if _NetworkConnector is None:
        _NetworkConnector = NetworkConnector('network_connector', 'AT_STARTUP', 4)
    if event is not None:
        _NetworkConnector.automat(event, arg)
    return _NetworkConnector


class NetworkConnector(Automat):
    timers = {'timer-1min':  (60,    ['DISCONNECTED']),
              'timer-1hour': (60*60, ['CONNECTED',])}

    def state_changed(self, oldstate, newstate):
        automats.set_global_state('NETWORK ' + newstate)
        p2p_connector.A('network_connector.state', newstate)

    def A(self, event, arg):
        #---AT_STARTUP---
        if self.state == 'AT_STARTUP':
            if event == 'init':
                self.doInit()
                self.doStun()
                self.state = 'STUN'
        #---STUN---
        elif self.state == 'STUN':
            if event == 'stun-success' and not self.isUPNP():
                self.state = 'CONNECTED'
            elif event == 'stun-success' and self.isUPNP():
                self.doUPNP()
                self.state = 'UPNP'
            elif event == 'stun-failed':
                self.state = 'DISCONNECTED'
        #---UPNP---
        elif self.state == 'UPNP':
            if event == 'upnp-done':
                self.state = 'CONNECTED'
        #---CONNECTED---
        elif self.state == 'CONNECTED':
            if ( event == 'cspace-status' and arg in ['offline', 'disconnecting'] ) or ( event == 'timer-1hour' and not self.isTrafficIN() ):
                self.doStun()
                self.state = 'STUN'
        #---DISCONNECTED---
        elif self.state == 'DISCONNECTED':
            if event == 'timer-1min' or ( event == 'cspace-status' and arg == 'online' ):
                self.doCallGoogle()
                self.state = 'GOOGLE?'
        #---GOOGLE?---
        elif self.state == 'GOOGLE?':
            if event == 'google-success':
                self.doStun()
                self.state = 'STUN'
            elif event == 'google-failed':
                self.state = 'DISCONNECTED'

    def isIPexternal(self):
        externalip = misc.readExternalIP()
        localip = misc.readLocalIP()
        return localip != externalip

    def isUPNP(self):
        return settings.enableUPNP()

    def isTrafficIN(self):
        return transport_control.TimeSinceLastReceive() < 60*10

    def doInit(self):
        if transport_control._TransportCSpaceEnable:
            transport_cspace.SetStatusNotifyFunc(cspace_status_changed)

    def doStun(self):
        def stun_success(externalip):
            if externalip == '0.0.0.0':
                self.automat('stun-failed')
                return
            localip = dhnnet.getLocalIp()
            dhnio.WriteFile(settings.ExternalIPFilename(), str(externalip))
            dhnio.WriteFile(settings.LocalIPFilename(), str(localip))
            self.automat('stun-success')
        def stun_failed(x):
            self.automat('stun-failed')
        stun.stunExternalIP(
            close_listener=False, 
            internal_port=settings.getUDPPort(),
            verbose=True if dhnio.Debug(10) else False).addCallbacks(stun_success, stun_failed)

    def doUPNP(self):
        UpdateUPNP()

    def doCallGoogle(self):
        if dhnnet.TestInternetConnection():
            self.automat('google-success')
        else:
            self.automat('google-failed')


def UpdateUPNP():
    #global _UpnpResult
    dhnio.Dprint(8, 'network_connector.UpdateUPNP ')

#    protos_need_upnp = set(['tcp', 'ssh', 'http'])
    protos_need_upnp = set(['tcp',])

    #we want to update only enabled protocols
    if not settings.enableTCP():
        protos_need_upnp.discard('tcp')
    if not settings.enableSSH() or not transport_control._TransportSSHEnable:
        protos_need_upnp.discard('ssh')
    if not settings.enableHTTPServer() or not transport_control._TransportHTTPEnable:
        protos_need_upnp.discard('http')

    dhnio.Dprint(6, 'network_connector.UpdateUPNP want to update protocols: ' + str(protos_need_upnp))

    def _update_next_proto():
        if len(protos_need_upnp) == 0:
            #dhnio.Dprint(4, 'network_connector.update_upnp done: ' + str(_UpnpResult))
            A('upnp-done')
            return
        dhnio.Dprint(14, 'network_connector.UpdateUPNP._update_next_proto ' + str(protos_need_upnp))
        proto = protos_need_upnp.pop()
        protos_need_upnp.add(proto)
        if proto == 'tcp':
            port = settings.getTCPPort()
        elif proto == 'ssh':
            port = settings.getSSHPort()
        elif proto == 'http':
            port = settings.getHTTPPort()
        d = threads.deferToThread(_call_upnp, port)
        d.addCallback(_upnp_proto_done, proto)

    def _call_upnp(port):
        # start messing with upnp settings
        # success can be false if you're behind a router that doesn't support upnp
        # or if you are not behind a router at all and have an external ip address
        shutdowner.A('block')
        success, port = run_upnpc.update(port)
        shutdowner.A('unblock')
        return (success, port)

    def _upnp_proto_done(result, proto):
        dhnio.Dprint(4, 'network_connector.UpdateUPNP._upnp_proto_done %s: %s' % (proto, str(result)))
        #_UpnpResult[proto] = result[0]
        #if _UpnpResult[proto] == 'upnp-done':
        if result[0] == 'upnp-done':
            if proto == 'tcp':
                settings.setTCPPort(result[1])
            elif proto == 'ssh':
                settings.setSSHPort(result[1])
            elif proto == 'http':
                settings.setHTTPPort(result[1])
        protos_need_upnp.discard(proto)
        reactor.callLater(0, _update_next_proto)

    _update_next_proto()


def cspace_status_changed(status):
    dhnio.Dprint(4, 'network_connector.cspace_status_changed [%s]' % status.upper())
    A('cspace-status', status)


