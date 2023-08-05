#!/usr/bin/python
#transport_udp.py
#
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2012
#    Use of this software constitutes acceptance of the Terms of Use
#      http://datahaven.net/terms_of_use.html
#    All rights reserved.
#
#

import os
import sys


from twisted.internet import reactor
from twisted.internet.task import LoopingCall 
from twisted.internet.defer import Deferred, succeed


import dhnio
import misc
import settings
import nameurl
import contacts
import identitycache

import stun
import shtoom.stun 
import shtoom.nat
                                                                 
import automat
import transport_udp_session 
import transport_udp_server     

_TransportUDP = None
_IsServer = False

#------------------------------------------------------------------------------ 

def init(client):
    A('init', client)
    

def shutdown():
    A('stop')
        
        
def send(filename, host, port, fast=False):
    # dhnio.Dprint(6, "transport_udp.send %s to %s:%s" % (os.path.basename(filename), host, port))
    A('send-file', ((host, int(port)), (filename, fast)))

def getListener():
    return A()

#------------------------------------------------------------------------------ 

def Start():
    A('start')
    
    
def Stop():
    A('stop')


def ListContactsCallback(oldlist, newlist):
    A('list-contacts', (oldlist, newlist))
    

def SendStatusCallback(host, filename, status, proto='', error=None, message=''):
    try:
        from transport_control import sendStatusReport
        sendStatusReport(host, filename, status, proto, error, message)
    except:
        dhnio.DprintException()


def ReceiveStatusCallback(filename, status, proto='', host=None, error=None, message=''):
    try:
        from transport_control import receiveStatusReport
        receiveStatusReport(filename, status, proto, host, error, message)
    except:
        dhnio.DprintException()

#------------------------------------------------------------------------------ 

def A(event=None, arg=None):
    global _TransportUDP
    if _TransportUDP is None:
        _TransportUDP = TransportUDP()
    if event is not None:
        _TransportUDP.automat(event, arg)
    return _TransportUDP


class TransportUDP(automat.Automat):
    def __init__(self):
        self.client = None
        self.index_by_idurl = {}
        automat.Automat.__init__(self, 'transport_udp', 'STOPPED', 4)
        
    def A(self, event, arg):
        #---STARTED---
        if self.state is 'STARTED':
            if event == 'send-file':
                self.doClientOutboxFile(arg)
            elif event == 'stop':
                self.doShutDownAllUDPSessions()
                self.doShutdownClient()
                self.state = 'STOPPED'
            elif event == 'list-contacts' and self.isNewUDPContact(arg):
                self.doRemoveOldUDPSession(arg)
                self.doCreateNewUDPSession(arg)
            elif event == 'ip-port-changed':
                self.doRestartUDPSession(arg)
        #---STOPPED---
        elif self.state is 'STOPPED':
            if event == 'init' and self.isOpenedIP(arg):
                self.doInitServer(arg)
                self.state = 'SERVER'
            elif event == 'init' and not self.isOpenedIP(arg):
                self.doInitClient(arg)
                self.state = 'CLIENT'
        #---SERVER---
        elif self.state is 'SERVER':
            if event == 'send-file':
                self.doServerOutboxFile(arg)
            elif event == 'stop':
                self.state = 'STOPPED'
        #---CLIENT---
        elif self.state is 'CLIENT':
            if event == 'start':
                self.doStartAllUDPSessions()
                self.state = 'STARTED'
            elif event == 'stop':
                self.doShutdownClient()
                self.state = 'STOPPED'

    def isOpenedIP(self, arg):
        if arg is None:
            return False
        return arg.externalAddress[0] == arg.localAddress

    def isNewUDPContact(self, arg):
        return arg[0] != arg[1]
    
    def doInitServer(self, arg):
        self.client = arg
        transport_udp_server.init(self.client)
        transport_udp_server.SetReceiveStatusCallback(ReceiveStatusCallback)
        transport_udp_server.SetSendStatusCallback(SendStatusCallback)
        
    def doInitClient(self, arg):
        self.client = arg
        self.client.datagram_received_callback = transport_udp_session.data_received
        transport_udp_session.SetReceiveStatusCallback(ReceiveStatusCallback)
        transport_udp_session.SetSendStatusCallback(SendStatusCallback)
        transport_udp_session.StartTimers()
        
    def doShutdownClient(self):
        transport_udp_session.StopTimers()
    
    def doStartAllUDPSessions(self):
        all = contacts.getContactsAndCorrespondents()
        all.append(settings.CentralID())
        # all.remove(misc.getLocalID())
        for idurl in all:
            ident = contacts.getContact(idurl)
            if ident is None:
                continue
            udp_contact = ident.getProtoContact('udp')
            if udp_contact is None:
                continue
            try:
                proto, host, port, filename = nameurl.UrlParse(udp_contact)
                udp_contact = (host, int(port))
            except:
                dhnio.DprintException()
                continue
            transport_udp_session.A(udp_contact, 'init', (self, idurl))
            self.index_by_idurl[idurl] = udp_contact
        
    def doShutDownAllUDPSessions(self):
        transport_udp_session.shutdown_all()
        self.index_by_idurl.clear()
    
    def doCreateNewUDPSession(self, arg):
        dhnio.Dprint(6, 'transport_udp.doRemoveOldUDPSession')
        for idurl in arg[1]:
            if idurl == misc.getLocalID():
                continue
            if idurl not in arg[0]:
                ident = contacts.getContact(idurl)
                if ident is None:
                    continue
                udp_contact = ident.getProtoContact('udp')
                if udp_contact is None:
                    continue
                try:
                    proto, host, port, filename = nameurl.UrlParse(udp_contact)
                    udp_contact = (host, int(port))
                except:
                    dhnio.DprintException()
                    continue
                dhnio.Dprint(6, 'transport_udp.doCreateNewUDPSession with %s [%s]' % (nameurl.GetName(idurl), str(udp_contact)))
                transport_udp_session.A(udp_contact, 'init', (self, idurl))
                self.index_by_idurl[idurl] = udp_contact
    
    def doRemoveOldUDPSession(self, arg):
        dhnio.Dprint(6, 'transport_udp.doRemoveOldUDPSession')
        for idurl in arg[0]:
            if idurl == misc.getLocalID():
                continue
            if idurl not in arg[1]:
                ident = contacts.getContact(idurl)
                if ident is None:
                    continue
                udp_contact = ident.getProtoContact('udp')
                if udp_contact is None:
                    continue
                try:
                    ip, port = udp_contact[6:].split(':')
                    udp_contact = (ip, int(port))
                except:
                    dhnio.DprintException()
                    continue
                if udp_contact in transport_udp_session.sessions():
                    dhnio.Dprint(6, 'transport_udp.doRemoveOldUDPSession with %s [%s]' % (nameurl.GetName(idurl), str(udp_contact)))
                    transport_udp_session.A(udp_contact, 'shutdown')
                    self.index_by_idurl.pop(idurl)
                
    def doRestartUDPSession(self, arg):
        idurl = arg
        ident = contacts.getContact(arg)
        if ident is None:
            return
        udp_contact = ident.getProtoContact('udp')
        if udp_contact is None:
            return
        try:
            ip, port = udp_contact[6:].split(':')
            udp_contact = (ip, int(port))
        except:
            dhnio.DprintException()
            return
        dhnio.Dprint(6, 'transport_udp.doRestartUDPSession with %s [%s]' % (nameurl.GetName(idurl), str(udp_contact)))
        transport_udp_session.A(udp_contact, 'init', (self, idurl))
        self.index_by_idurl[idurl] = udp_contact
                
    def doReceiveDataProcess(self, arg):
        transport_udp_session.A(arg[1], 'datagram-received', arg[0])
        
    def doServerOutboxFile(self, arg):
        transport_udp_server.send(arg[0], arg[1][0], arg[1][1])    
        
    def doClientOutboxFile(self, arg):
        transport_udp_session.outbox_file(arg[0], arg[1][0], arg[1][1])
    
    def stopListening(self):
        dhnio.Dprint(4, 'transport_udp.stopListening')
        self.automat('stop')
        res = stun.stopUDPListener()
        if res is None:
            res = succeed(1)
        return res

#------------------------------------------------------------------------------ 

def main():
    sys.path.append('..')
    def _start_sending():
        if len(sys.argv) >= 4:
            LoopingCall(send, sys.argv[2], sys.argv[3], int(sys.argv[4])).start(60, False)
    def _id_sent(x):
        init()
        Start()
        _start_sending()
    def _stuned(ip):
        if stun.getUDPClient() is None:
            reactor.stop()
            return
        init(stun.getUDPClient())
        _start_sending()
#            #else:
#            #    d.addBoth(lambda x: init(True, int(sys.argv[1])))
#        else:
#            lid = misc.getLocalIdentity()
#            udp_contact = 'udp://'+stun.getUDPClient().externalAddress[0]+':'+str(stun.getUDPClient().externalAddress[1])
#            lid.setProtoContact('udp', udp_contact)
#            lid.sign()
#            misc.setLocalIdentity(lid)
#            misc.saveLocalIdentity()
#            dhnio.Dprint(4, 'UpdateIdentity %s' % str(lid.contacts))
#            import p2p.identitypropagate
#            p2p.identitypropagate.update().addBoth(_id_sent)
    dhnio.SetDebug(14)
    # dhnio.LifeBegins()
    contacts.init()
    identitycache.init()
    stun.stunExternalIP(
        close_listener=False, 
        internal_port=sys.argv[1],
        verbose=False).addBoth(_stuned)

#------------------------------------------------------------------------------ 

if __name__ == '__main__':
    if len(sys.argv) not in [2,5]:
        print 'transport_udp.py <listening PORT> [filename] [host] [port]'
        sys.exit(0)
        
    main()
    reactor.run()

