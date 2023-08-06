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
import time


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

def init(client,):
    dhnio.Dprint(4, 'transport_udp.init ' + str(client))
    A('init', client)
    

def shutdown():
    A('stop')
    
# fast=True: put filename in the top of sending queue,
# fast=False: append to the bottom of the queue    
def send(filename, host, port, fast=False):
    # dhnio.Dprint(6, "transport_udp.send %s to %s:%s" % (os.path.basename(filename), host, port))
    A('send-file', ((host, int(port)), (filename, fast)))

def getListener():
    return A()

#------------------------------------------------------------------------------ 

class TransferInfo():
    def __init__(self, remote_address, filename, size):
        self.remote_address = remote_address
        self.filename = filename
        self.size = size

def current_transfers():
    return A().currentTransfers()

#------------------------------------------------------------------------------ 

def Start():
    A('start')
    
    
def Stop():
    A('stop')


def ListContactsCallback(oldlist, newlist):
    A('list-contacts', (oldlist, newlist))
    
#------------------------------------------------------------------------------ 

def SendStatusCallbackDefault(host, filename, status, proto='', error=None, message=''):
    try:
        from transport_control import sendStatusReport
        return sendStatusReport(host, filename, status, proto, error, message)
    except:
        dhnio.DprintException()
        return None

def ReceiveStatusCallbackDefault(filename, status, proto='', host=None, error=None, message=''):
    try:
        from transport_control import receiveStatusReport
        return receiveStatusReport(filename, status, proto, host, error, message)
    except:
        dhnio.DprintException()
        return None

def SendControlFuncDefault(prev_read_size, chunk_size):
    try:
        from transport_control import SendTrafficControl
        return SendTrafficControl(prev_read_size, chunk_size)
    except:
        dhnio.DprintException()
        return chunk_size
        
def ReceiveControlFuncDefault(new_data_size):
    try:
        from transport_control import ReceiveTrafficControl
        return ReceiveTrafficControl(new_data_size)
    except:
        dhnio.DprintException()
        return 0
    
def RegisterTransferFuncDefault(send_or_receive, remote_address, callback, filename, size):
    try:
        from transport_control import register_transfer
        return register_transfer('udp', send_or_receive, remote_address, callback, filename, size)
    except:
        dhnio.DprintException()
    return None
    
def UnRegisterTransferFuncDefault(transfer_id):
    try:
        from transport_control import unregister_transfer
        return unregister_transfer(transfer_id)
    except:
        dhnio.DprintException()
    return None

#------------------------------------------------------------------------------ 

def A(event=None, arg=None):
    global _TransportUDP
    if _TransportUDP is None:
        _TransportUDP = TransportUDP()
    if event is not None:
        _TransportUDP.automat(event, arg)
    return _TransportUDP

#------------------------------------------------------------------------------ 

class TransportUDP(automat.Automat):
    def __init__(self):
        self.client = None
        self.transfers = {}
        self.debug = False
        automat.Automat.__init__(self, 'transport_udp', 'STOPPED', 6)
        
    def A(self, event, arg):
        #---STARTED---
        if self.state is 'STARTED':
            if event == 'send-file' :
                self.doClientOutboxFile(arg)
            elif event == 'stop' :
                self.doShutDownAllUDPSessions(arg)
                self.doShutdownClient(arg)
                self.state = 'STOPPED'
            elif event == 'list-contacts' and self.isNewUDPContact(arg) :
                self.doRemoveOldUDPSession(arg)
                self.doCreateNewUDPSession(arg)
            elif event == 'ip-port-changed' :
                self.doRestartUDPSession(arg)
        #---STOPPED---
        elif self.state is 'STOPPED':
            if event == 'init' and self.isOpenedIP(arg) :
                self.doInitServer(arg)
                self.state = 'SERVER'
            elif event == 'init' and not self.isOpenedIP(arg) :
                self.doInitClient(arg)
                self.state = 'CLIENT'
        #---SERVER---
        elif self.state is 'SERVER':
            if event == 'send-file' :
                self.doServerOutboxFile(arg)
            elif event == 'stop' :
                self.state = 'STOPPED'
        #---CLIENT---
        elif self.state is 'CLIENT':
            if event == 'start' :
                self.doStartAllUDPSessions(arg)
                self.state = 'STARTED'
            elif event == 'stop' :
                self.doShutdownClient(arg)
                self.state = 'STOPPED'

    def isOpenedIP(self, arg):
        if not arg:
            return False
        if not arg.externalAddress:
            return False
        if not arg.localAddress:
            return False            
        return arg.externalAddress[0] == arg.localAddress

    def isNewUDPContact(self, arg):
        return arg[0] != arg[1]
    
    def doInitServer(self, arg):
        self.client = arg
        transport_udp_server.init(self.client)
        # self.client.datagram_received_callback = self.datagramReceived
        self.client.datagram_received_callback = transport_udp_server.protocol().datagramReceived
        transport_udp_server.SetReceiveStatusCallback(ReceiveStatusCallbackDefault)
        transport_udp_server.SetSendStatusCallback(SendStatusCallbackDefault)
        transport_udp_server.SetReceiveControlFunc(ReceiveControlFuncDefault)
        transport_udp_server.SetSendControlFunc(SendControlFuncDefault)
        transport_udp_server.SetRegisterTransferFunc(RegisterTransferFuncDefault)
        transport_udp_server.SetUnRegisterTransferFunc(UnRegisterTransferFuncDefault)
        
    def doInitClient(self, arg):
        self.client = arg
        # self.client.datagram_received_callback = self.datagramReceived
        self.client.datagram_received_callback = transport_udp_session.data_received
        transport_udp_session.init(self)
        transport_udp_session.SetReceiveStatusCallback(ReceiveStatusCallbackDefault)
        transport_udp_session.SetSendStatusCallback(SendStatusCallbackDefault)
        transport_udp_session.SetReceiveControlFunc(ReceiveControlFuncDefault)
        transport_udp_session.SetSendControlFunc(SendControlFuncDefault)
        transport_udp_session.SetRegisterTransferFunc(RegisterTransferFuncDefault)
        transport_udp_session.SetUnRegisterTransferFunc(UnRegisterTransferFuncDefault)
        
    def doShutdownClient(self, arg):
        transport_udp_session.shutdown()
    
    def doStartAllUDPSessions(self, arg):
        all = contacts.getContactsAndCorrespondents()
        if not self.debug:
            all.append(settings.CentralID())
        for idurl in all:
            ident = contacts.getContact(idurl)
            if ident is None:
                continue
            address = ident.getProtoContact('udp')
            if address is None:
                continue
            try:
                proto, ip, port, filename = nameurl.UrlParse(address)
                address = (ip, int(port))
            except:
                dhnio.DprintException()
                continue
            address = self.remapAddress(address)
            transport_udp_session.A(address, 'init', idurl)
        
    def doShutDownAllUDPSessions(self, arg):
        transport_udp_session.shutdown_all()
    
    def doRemoveOldUDPSession(self, arg):
        for idurl in arg[0]:
            if idurl == misc.getLocalID():
                continue
            if idurl not in arg[1]:
                ident = contacts.getContact(idurl)
                if ident is None:
                    continue
                address = ident.getProtoContact('udp')
                if address is None:
                    continue
                try:
                    ip, port = address[6:].split(':')
                    address = (ip, int(port))
                except:
                    dhnio.DprintException()
                    continue
                if transport_udp_session.is_session_opened(address, idurl):
                    dhnio.Dprint(6, 'transport_udp.doRemoveOldUDPSession with %s [%s]' % (nameurl.GetName(idurl), str(address)))
                    transport_udp_session.A(address, 'shutdown')
                address_local = self.remapAddress(address)
                if address_local != address:
                    if transport_udp_session.is_session_opened(address, idurl):
                        dhnio.Dprint(6, 'transport_udp.doRemoveOldUDPSession with %s [%s]' % (nameurl.GetName(idurl), str(address)))
                        transport_udp_session.A(address, 'shutdown')
                
    def doCreateNewUDPSession(self, arg):
        for idurl in arg[1]:
            if idurl == misc.getLocalID():
                continue
            if idurl not in arg[0]:
                ident = contacts.getContact(idurl)
                if ident is None:
                    continue
                address = ident.getProtoContact('udp')
                if address is None:
                    continue
                try:
                    proto, ip, port, filename = nameurl.UrlParse(address)
                    address = (ip, int(port))
                except:
                    dhnio.DprintException()
                    continue
                address = self.remapAddress(address)
                dhnio.Dprint(6, 'transport_udp.doCreateNewUDPSession with %s [%s]' % (nameurl.GetName(idurl), str(address)))
                transport_udp_session.A(address, 'init', idurl)
    
    def doRestartUDPSession(self, arg):
        idurl = arg
        ident = contacts.getContact(idurl)
        if ident is None:
            return
        address = ident.getProtoContact('udp')
        if address is None:
            return
        try:
            ip, port = address[6:].split(':')
            address = (ip, int(port))
        except:
            dhnio.DprintException()
            return
        address = self.remapAddress(address)
        dhnio.Dprint(6, 'transport_udp.doRestartUDPSession with %s [%s]' % (nameurl.GetName(idurl), str(address)))
        transport_udp_session.A(address, 'init', idurl)
                
    def doServerOutboxFile(self, arg):
        transport_udp_server.send(arg[0], arg[1][0], arg[1][1])    
        
    def doClientOutboxFile(self, arg):
        address = arg[0]
        idurls = identitycache.GetIDURLsByContact('udp://%s:%d' % (address[0], address[1]))
        if len(idurls) > 0:
            idurl = idurls[0] 
            address = self.remapAddress(address)
            transport_udp_session.outbox_file(address, idurl, arg[1][0], arg[1][1])
        else:
            dhnio.Dprint(2, 'transport_udp.doClientOutboxFile WARNIMG unknown address: ' + str(address))

    def stopListening(self):
        dhnio.Dprint(4, 'transport_udp.stopListening')
        self.automat('stop')
        res = stun.stopUDPListener()
        if res is None:
            res = succeed(1)
        return res

    # use local IP instead of external if it comes from central server 
    def remapAddress(self, address):
        return identitycache.RemapContactAddress(address)
    
#------------------------------------------------------------------------------ 

def main():
    sys.path.append('..')

    def _go_stun(port):
        print '+++++ LISTEN UDP ON PORT', port, 'AND RUN STUN DISCOVERY'
        stun.stunExternalIP(close_listener=False, internal_port=port, verbose=False).addBoth(_stuned)

    def _stuned(ip):
        if stun.getUDPClient() is None:
            print 'UDP CLIENT IS NONE - EXIT'
            reactor.stop()
            return

        print '+++++ EXTERNAL UDP ADDRESS IS', stun.getUDPClient().externalAddress
        
        if sys.argv[1] == 'listen':
            print '+++++ START LISTENING'
            return
        
        if sys.argv[1] == 'connect':
            print '+++++ CONNECTING TO REMOTE MACHINE'
            _try2connect()
            return

        lid = misc.getLocalIdentity()
        udp_contact = 'udp://'+stun.getUDPClient().externalAddress[0]+':'+str(stun.getUDPClient().externalAddress[1])
        lid.setProtoContact('udp', udp_contact)
        lid.sign()
        misc.setLocalIdentity(lid)
        misc.saveLocalIdentity()
        
        print '+++++ UPDATE IDENTITY', str(lid.contacts)
        import p2p.identitypropagate
        p2p.identitypropagate.update().addBoth(_id_sent)

    def _try2connect():
        remote_addr = dhnio.ReadTextFile(sys.argv[3]).split(' ')
        remote_addr = (remote_addr[0], int(remote_addr[1]))
        t = int(str(int(time.time()))[-1]) + 1
        data = '0' * t
        stun.getUDPClient().transport.write(data, remote_addr)
        print 'sent %d bytes to %s' % (len(data), str(remote_addr))
        reactor.callLater(1, _try2connect)

    def _id_sent(x):
        print '+++++ ID UPDATED ON THE SERVER'
        if sys.argv[1] == 'send':
            _start_sending()
        elif sys.argv[1] == 'receive':
            _start_receiving()

    def _start_receiving():
        idurl = sys.argv[2]
        if not idurl.startswith('http://'):
            idurl = 'http://'+settings.IdentityServerName()+'/'+idurl+'.xml'
        print '+++++ START RECEIVING FROM', idurl
        _request_remote_id(idurl).addBoth(_receive_from_remote_peer, idurl)
        
    def _receive_from_remote_peer(x, idurl):
        init(stun.getUDPClient())
        A().debug = True
        contacts.addCorrespondent(idurl)
        reactor.callLater(1, Start)

    def _start_sending():
        idurl = sys.argv[2]
        if not idurl.startswith('http://'):
            idurl = 'http://'+settings.IdentityServerName()+'/'+idurl+'.xml'
        print '+++++ START SENDING TO', idurl
#        if len(sys.argv) == 6:
#            send(sys.argv[5], sys.argv[3], int(sys.argv[4]))
#        elif len(sys.argv) == 4:
        _request_remote_id(idurl).addBoth(_send_to_remote_peer, idurl, sys.argv[3])

    def _request_remote_id(idurl):
        print '+++++ REQUEST ID FROM SERVER', idurl
        return identitycache.immediatelyCaching(idurl)
    
    def _send_to_remote_peer(x, idurl, filename):
        init(stun.getUDPClient())
        A().debug = True
        reactor.callLater(1, Start)
        ident = identitycache.FromCache(idurl)
        if ident is None:
            print '+++++ REMOTE IDENTITY IS NONE'
            reactor.stop()
        x, udphost, udpport, x = ident.getProtoParts('udp')
        print '+++++ START SENDING TO', udphost, udpport
        reactor.callLater(2, send, filename, udphost, udpport)
    
    
    dhnio.SetDebug(20)
    dhnio.LifeBegins()
    settings.init()
    misc.loadLocalIdentity()
    # contacts.init()
    # contacts.addCorrespondent(idurl)
    identitycache.init()
    port = int(settings.getUDPPort())
    if sys.argv[1] in ['listen', 'connect']:
        port = int(sys.argv[2])
    _go_stun(port)

#------------------------------------------------------------------------------ 

if __name__ == '__main__':
    if len(sys.argv) not in [2, 3, 4, 6] or sys.argv[1] not in ['send', 'receive', 'listen', 'connect']:
        print 'transport_udp.py receive <from username>'
        print 'transport_udp.py receive <from idurl>'
        print 'transport_udp.py send <to username> <filename>'
        print 'transport_udp.py send <to idurl> <filename>'
        print 'transport_udp.py listen <listening port>'
        print 'transport_udp.py connect <listening port> <filename with remote address>'
        sys.exit(0)
        
    main()
    reactor.run()



