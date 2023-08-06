#!/usr/bin/env python
#network_connector.py
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
    sys.exit('Error initializing twisted.internet.reactor in network_connector.py')

from twisted.internet.defer import Deferred, maybeDeferred
from twisted.internet.task import LoopingCall
from twisted.internet import threads

from lib.automat import Automat
import lib.automats as automats

import lib.dhnio as dhnio
import lib.dhnnet as dhnnet
import lib.misc as misc
import lib.settings as settings
import lib.stun as stun
import lib.transport_control as transport_control
if transport_control._TransportCSpaceEnable:
    import lib.transport_cspace as transport_cspace

import p2p_connector
import central_connector
import shutdowner

import dhnicon
import run_upnpc


_NetworkConnector = None
_CounterSuccessConnections = 0
_CounterFailedConnections = 0
_FlagSuccessActivity = False

#------------------------------------------------------------------------------

def A(event=None, arg=None):
    global _NetworkConnector
    if _NetworkConnector is None:
        _NetworkConnector = NetworkConnector('network_connector', 'AT_STARTUP', 4)
    if event is not None:
        _NetworkConnector.automat(event, arg)
    return _NetworkConnector


class NetworkConnector(Automat):
    timers = { 'timer-5sec':  (10,    ['CONNECTED', 'DISCONNECTED'])}

    def state_changed(self, oldstate, newstate):
        automats.set_global_state('NETWORK ' + newstate)
        p2p_connector.A('network_connector.state', newstate)
        dhnicon.state_changed(self.state, p2p_connector.A().state, central_connector.A().state)

    def A(self, event, arg):
        #---AT_STARTUP---
        if self.state is 'AT_STARTUP':
            if event == 'init' :
                self.doInit(arg)
                self.doStunExternalIP(arg)
                self.state = 'STUN'
        #---STUN---
        elif self.state is 'STUN':
            if event == 'stun-success' and not self.isUPNP(arg) :
                self.doDropCounters(arg)
                self.state = 'CONNECTED'
            elif event == 'stun-success' and self.isUPNP(arg) :
                self.doUPNP(arg)
                self.state = 'UPNP'
            elif event == 'stun-failed' :
                self.state = 'DISCONNECTED'
        #---UPNP---
        elif self.state is 'UPNP':
            if event == 'upnp-done' :
                self.doDropCounters(arg)
                self.state = 'CONNECTED'
        #---CONNECTED---
        elif self.state is 'CONNECTED':
            if event == 'timer-5sec' and self.isConnectionAlive(arg) :
                self.doDropCounters(arg)
            elif event == 'timer-5sec' and not self.isConnectionAlive(arg) :
                self.doDropCounters(arg)
                self.doCheckNetworkInterfaces(arg)
                self.state = 'NETWORK?'
        #---NETWORK?---
        elif self.state is 'NETWORK?':
            if event == 'got-network-info' and not self.isNetworkActive(arg) :
                self.state = 'DISCONNECTED'
            elif event == 'got-network-info' and self.isNetworkActive(arg) and self.isCurrentInterfaceActive(arg) :
                self.doCallGoogle(arg)
                self.state = 'GOOGLE?'
            elif event == 'got-network-info' and self.isNetworkActive(arg) and not self.isCurrentInterfaceActive(arg) :
                self.doStunExternalIP(arg)
                self.state = 'STUN'
        #---GOOGLE?---
        elif self.state is 'GOOGLE?':
            if event == 'google-success' :
                self.doStunExternalIP(arg)
                self.state = 'STUN'
            elif event == 'google-failed' :
                self.state = 'DISCONNECTED'
        #---DISCONNECTED---
        elif self.state is 'DISCONNECTED':
            if event == 'timer-5sec' :
                self.doCheckNetworkInterfaces(arg)
                self.state = 'NETWORK?'

    def isUPNP(self, arg):
        return settings.enableUPNP()

#    def isTrafficIN(self):
#        return transport_control.TimeSinceLastReceive() < 60*10

    def isConnectionAlive(self, arg):
        global _CounterSuccessConnections
        global _CounterFailedConnections
        if _CounterSuccessConnections == 0:
            if _CounterFailedConnections == 0:
                return True
        if _CounterFailedConnections <= 3:
            return True
        if _CounterSuccessConnections >= 3:
            return True
        if _CounterSuccessConnections > _CounterFailedConnections:
            return True
        dhnio.Dprint(6, 'network_connector.isConnectionAlive %d/%d' % (_CounterSuccessConnections, _CounterFailedConnections) )
        return False

    def isNetworkActive(self, arg):
        return len(arg) > 0
    
    def isCurrentInterfaceActive(self, arg):
        return misc.readLocalIP() in arg

    def doInit(self, arg):
        # if transport_control._TransportCSpaceEnable:
        #     transport_cspace.SetStatusNotifyFunc(cspace_status_changed)
        dhnnet.SetConnectionDoneCallbackFunc(ConnectionDoneCallback)
        dhnnet.SetConnectionFailedCallbackFunc(ConnectionFailedCallback)

    def doStunExternalIP(self, arg):
        def stun_success(externalip):
            if externalip == '0.0.0.0':
                ConnectionFailedCallback()
                self.automat('stun-failed')
                return
            localip = dhnnet.getLocalIp()
            dhnio.WriteFile(settings.ExternalIPFilename(), str(externalip))
            dhnio.WriteFile(settings.LocalIPFilename(), str(localip))
            ConnectionDoneCallback()
            self.automat('stun-success')
        def stun_failed(x):
            ConnectionFailedCallback()
            self.automat('stun-failed')
        stun.stunExternalIP(
            close_listener=False, 
            internal_port=settings.getUDPPort(),
            verbose=True if dhnio.Debug(10) else False).addCallbacks(stun_success, stun_failed)

    def doDropCounters(self, arg):
        global _CounterSuccessConnections
        global _CounterFailedConnections
        _CounterSuccessConnections = 0
        _CounterFailedConnections = 0

    def doUPNP(self, arg):
        UpdateUPNP()

    def doCallGoogle(self, arg):
        if dhnnet.TestInternetConnection():
            self.automat('google-success')
        else:
            self.automat('google-failed')
            
    def doCheckNetworkInterfaces(self, arg):
        dhnio.Dprint(4, 'network_connector.doCheckNetworkInterfaces')
#        def _call():
#            return dhnnet.getNetworkInterfaces()
#        def _done(result, start_time):
#            dhnio.Dprint(4, 'network_connector.doCheckNetworkInterfaces._done: %s in %d seconds' % (str(result), time.time()- start_time))
#            self.automat('got-network-info', result)
#        tm = time.time()
#        d = threads.deferToThread(_call)
#        d.addBoth(_done, tm)
        ips = dhnnet.getNetworkInterfaces()
        self.automat('got-network-info', ips)


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


def ConnectionDoneCallback():
    global _FlagSuccessActivity
    global _CounterSuccessConnections 
    _FlagSuccessActivity = True
    _CounterSuccessConnections += 1
    
    
def ConnectionFailedCallback():
    global _CounterFailedConnections
    _CounterFailedConnections += 1




