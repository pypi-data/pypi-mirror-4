#!/usr/bin/env python

# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

import os
import sys

from twisted.internet.task import LoopingCall 
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

import dhnio
import stun

#class PublicUDPServer(DatagramProtocol):
#    def datagramReceived(self, datagram, host):
#        print 'received %d bytes from %s' % (len(datagram), host)
#        if datagram.startswith('test'):
#            self.transport.write('%s:%s' % (host[0], host[1]), host)
#    def send(self, data, address):
#        print 'send %d bytes to %s' % (len(data), address)
#        self.transport.write(data, address)

def main():
    dhnio.SetDebug(18)
    def _dgRcv(datagram, host):
        print 'received %d bytes:[%s] from %s' % (len(datagram), datagram[:128], host)
        if datagram.startswith('test'):
            stun.getUDPClient().transport.write('%s:%s' % (host[0], host[1]), host)
    def _check():
        to = dhnio.ReadTextFile('to').strip()
        if to:
            host, port = to.split(':')
            stun.getUDPClient().transport.write('test', (host, int(port)))
            print 'send "test" to %s' % to
    def _start(x):
        stun.getUDPClient().datagram_received_callback = _dgRcv
        LoopingCall(_check).start(5, False)
    stun.stunExternalIP(close_listener=False, internal_port=int(sys.argv[1])).addBoth(_start)
    
    #t = reactor.listenUDP(int(sys.argv[1]), PublicUDPServer())
        #p = TestClient()
        #l = reactor.listenUDP(int(sys.argv[2]), p)
#    protocol = PublicUDPServer()
#    if len(sys.argv) >= 3:
#        protocol.addr[0] = sys.argv[1]
#        protocol.addr[1] = int(sys.argv[2])
    reactor.run()

if __name__ == '__main__':
    main()
