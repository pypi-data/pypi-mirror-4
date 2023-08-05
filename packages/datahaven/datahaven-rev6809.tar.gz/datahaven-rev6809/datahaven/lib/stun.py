#!/usr/bin/python
#stun.py
#
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2012
#    All rights reserved.
#
#

import sys
import sets
import struct


try:
    from twisted.internet import reactor
except:
    sys.exit('Error initializing twisted.internet.reactor in stun.py')

from twisted.internet.defer import Deferred, succeed, fail
from twisted.python import log

import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)


import shtoom.stun
import shtoom.nat
import dhnio


_WorkingDefer = None
_UDPListener = None
_TimeOutTask = None
_StunClient = None

#------------------------------------------------------------------------------ 

class IPStunProtocol(shtoom.stun.StunDiscoveryProtocol):
    datagram_received_callback = None

    def finishedStun(self):
        try:
            ip = str(self.externalAddress[0])
            port = str(self.externalAddress[1])
            typ = str(self.natType.name)
        except:
            ip = '0.0.0.0'
            port = '0'
            typ = 'unknown'
        dhnio.Dprint(4, 'stun.IPStunProtocol.finishedStun local=%s external=%s altStun=%s NAT_type=%s' % (
            str(self.localAddress), str(self.externalAddress), str(self._altStunAddress), str(self.natType)))
        if self.result is not None:
            if not self.result.called:
                if ip == '0.0.0.0':
                    self.result.errback(ip)
                else:
                    self.result.callback(ip)
            self.result = None

    def _hostNotResolved(self, x):
        dhnio.Dprint(2, 'stun.IPStunProtocol._hostNotResolved ' + x.getErrorMessage())
        self.count += 1
        if self.count >= len(shtoom.stun.DefaultServers) / 2:
            if self.result is not None:
                if not self.result.called:
                    self.result.errback(x)
                self.result = None
    
    def datagramReceived(self, dgram, address):
        if self._finished:
            if self.datagram_received_callback is not None:
                return self.datagram_received_callback(dgram, address)
        else:
            stun_dgram = dgram[:20]
            if len(stun_dgram) < 20:
                if self.datagram_received_callback is None:
                    return
                return self.datagram_received_callback(dgram, address)
            else:
                try:
                    mt, pktlen, tid = struct.unpack('!hh16s', stun_dgram)
                except:
                    if self.datagram_received_callback is None:
                        return
                    return self.datagram_received_callback(dgram, address)
        return shtoom.stun.StunDiscoveryProtocol.datagramReceived(self, dgram, address)
    
    def refresh(self):
        self._potentialStuns = {}
        self._stunState = '1'
        self._finished = False
        self._altStunAddress = None
        self.externalAddress = None
        self.localAddress = None
        self.expectedTID = None
        self.oldTIDs = sets.Set()
        self.natType = None
        self.result = Deferred()
        self.count = 0
        self.servers = [(host, port) for host, port in shtoom.stun.DefaultServers]
        
    def setCallback(self, cb):
        self.result.addBoth(cb)


def stunExternalIP(timeout=60, verbose=False, close_listener=True, internal_port=5061):
    global _WorkingDefer
    global _UDPListener
    global _StunClient
    global _TimeOutTask
    if _WorkingDefer is not None:
        dhnio.Dprint(4, 'stun.stunExternalIP WARNING already called')
        return _WorkingDefer
    _WorkingDefer = Deferred()

    dhnio.Dprint(4, 'stun.stunExternalIP')

    shtoom.stun.STUNVERBOSE = verbose
    shtoom.nat._Debug = verbose
    shtoom.nat._cachedLocalIP = None
    shtoom.nat.getLocalIPAddress.clearCache()
    
    if _UDPListener is None:
        dhnio.Dprint(4, 'stun.stunExternalIP prepare listener')
        if _StunClient is None:
            _StunClient = IPStunProtocol()
        else:
            _StunClient.refresh()
    
        try:
            UDP_port = int(internal_port)
            _UDPListener = reactor.listenUDP(UDP_port, _StunClient)
            dhnio.Dprint(4, 'stun.stunExternalIP UDP listening on port %d started' % UDP_port)
        except:
            try:
                _UDPListener = reactor.listenUDP(0, _StunClient)
                dhnio.Dprint(4, 'stun.stunExternalIP multi-cast UDP listening started')
            except:
                dhnio.DprintException()
                _WorkingDefer = None
                return fail('0.0.0.0')

    dhnio.Dprint(6, 'stun.stunExternalIP refresh stun client')
    _StunClient.refresh()

    def stun_finished(x):
        global _UDPListener
        global _TimeOutTask
        global _StunClient
        global _WorkingDefer
        dhnio.Dprint(6, 'stun.stunExternalIP.stun_finished: ' + str(x).replace('\n', ''))
        try:
            if _WorkingDefer:
                if x == '0.0.0.0':
                    _WorkingDefer.errback(x)
                else:
                    _WorkingDefer.callback(x)
            _WorkingDefer = None
            if _UDPListener is not None and close_listener is True:
                _UDPListener.stopListening()
                _UDPListener = None
            if _TimeOutTask:
                if not _TimeOutTask.called:
                    _TimeOutTask.cancel()
                _TimeOutTask = None
            if _StunClient is not None and close_listener is True:
                del _StunClient
                _StunClient = None
        except:
            dhnio.DprintException()

    def time_out():
        global _StunClient
        dhnio.Dprint(6, 'stun.stunExternalIP.time_out')
        if _StunClient:
            if _StunClient.result:
                if not _StunClient.result.called:
                    _StunClient.result.errback('0.0.0.0')

    _StunClient.setCallback(stun_finished)

    _TimeOutTask = reactor.callLater(timeout, time_out)
    
    dhnio.Dprint(6, 'stun.stunExternalIP starting discovery')
    reactor.callLater(0, _StunClient.startDiscovery)

    return _WorkingDefer


def getUDPListener():
    global _UDPListener
    return _UDPListener


def getUDPClient():
    global _StunClient
    return _StunClient


def stopUDPListener():
    dhnio.Dprint(6, 'stun.stopUDPListener')
    global _UDPListener
    global _StunClient
    result = None
    if _UDPListener is not None:
        result = _UDPListener.stopListening()
        _UDPListener = None
    if _StunClient is not None:
        del _StunClient
        _StunClient = None   
    if result is None:
        result = succeed(1)
    return result     

#------------------------------------------------------------------------------ 

def success(x):
    print 'stun.success', x
    reactor.callLater(10, main)
    #reactor.stop()

def fail(x):
    print 'stun.fail', x
    reactor.callLater(5, main)
    #reactor.stop()

def main(verbose=False):
    if len(sys.argv) > 1:
        d = stunExternalIP(verbose=verbose, close_listener=False, internal_port=int(sys.argv[1]))
    else:
        d = stunExternalIP(verbose=verbose, close_listener=False,)
    d.addCallback(success)
    d.addErrback(fail)


if __name__ == "__main__":
#    log.startLogging(sys.stdout)
    dhnio.SetDebug(14)
    main(False)
    reactor.run()






