#!/usr/bin/python
#transport_udp.py
#
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2013
#    Use of this software constitutes acceptance of the Terms of Use
#      http://datahaven.net/terms_of_use.html
#    All rights reserved.
#
#

import os
import sys
import time
import random

from twisted.internet import reactor
from twisted.internet.task import LoopingCall 
from twisted.internet.defer import Deferred, DeferredList, succeed


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
def send(filename, host, port, fast=False, description=''):
    # dhnio.Dprint(6, "transport_udp.send %s to %s:%s" % (os.path.basename(filename), host, port))
    A('send-file', ((host, int(port)), (filename, fast, description)))

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
    
def RegisterTransferFuncDefault(send_or_receive, remote_address, callback, filename, size, description):
    try:
        from transport_control import register_transfer
        return register_transfer('udp', send_or_receive, remote_address, callback, filename, size, description)
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
                self.state = 'STOPPED'
                self.doShutDownAllUDPSessions(arg)
                self.doShutdownClient(arg)
            elif event == 'list-contacts' and self.isNewUDPContact(arg) :
                self.doRemoveOldUDPSession(arg)
                self.doCreateNewUDPSession(arg)
            elif event == 'child-request-remote-id' :
                self.doRequestRemoteID(arg)
            elif event == 'remote-id-received' and self.isIPPortChanged(arg) :
                self.doRestartUDPSession(arg)
            elif event == 'child-request-recreate' :
                self.doRecreateUDPSession(arg)
            elif event == 'recognize-remote-id' :
                self.doCloseDuplicatedUDPSession(arg)
        #---STOPPED---
        elif self.state is 'STOPPED':
            if event == 'init' and self.isOpenedIP(arg) :
                self.state = 'SERVER'
                self.doInitServer(arg)
            elif event == 'init' and not self.isOpenedIP(arg) :
                self.state = 'CLIENT'
                self.doInitClient(arg)
        #---SERVER---
        elif self.state is 'SERVER':
            if event == 'send-file' :
                self.doServerOutboxFile(arg)
            elif event == 'stop' :
                self.state = 'STOPPED'
        #---CLIENT---
        elif self.state is 'CLIENT':
            if event == 'start' :
                self.state = 'STARTED'
                self.doStartAllUDPSessions(arg)
            elif event == 'stop' :
                self.state = 'STOPPED'
                self.doShutdownClient(arg)

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
    
    def isIPPortChanged(self, arg):
        idurl = arg
        ident = contacts.getContact(idurl)
        if ident is None:
            return False
        address = ident.getProtoContact('udp')
        if address is None:
            return False
        try:
            ip, port = address[6:].split(':')
            address = (ip, int(port))
        except:
            dhnio.DprintException()
            return False
        address_local = self.remapAddress(address)
        found = False
        for sess in transport_udp_session.sessions():
            if  sess.remote_idurl is not None and \
                sess.remote_idurl == idurl and \
                ( sess.remote_address[0] == address[0] or sess.remote_address[0] == address_local[0] ) and \
                ( sess.remote_address[1] != address[1] and sess.remote_address[1] != address_local[1] ):
                found = True
                dhnio.Dprint(6, 'transport_udp.isIPPortChanged found related session %s with [%s]' % (sess.name, sess.remote_name))
        return found        
    
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
            sess = transport_udp_session.open_session(address)
            dhnio.Dprint(8, 'transport_udp.doStartAllUDPSessions init %s with [%s]' % (sess.name, nameurl.GetName(idurl)))
            sess.automat('init', idurl)
        
    def doShutDownAllUDPSessions(self, arg):
        transport_udp_session.shutdown_all_sessions()
    
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
                if transport_udp_session.is_session_opened(address):
                    dhnio.Dprint(8, 'transport_udp.doRemoveOldUDPSession shutdown %s with [%s]' % (str(address), nameurl.GetName(idurl)))
                    reactor.callLater(0, transport_udp_session.A, address, 'shutdown')
                address_local = self.remapAddress(address)
                if address_local != address:
                    if transport_udp_session.is_session_opened(address_local):
                        dhnio.Dprint(8, 'transport_udp.doRemoveOldUDPSession shutdown %s with local peer [%s]' % (str(address_local), nameurl.GetName(idurl)))
                        reactor.callLater(0, transport_udp_session.A, address_local, 'shutdown')
                
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
                sess = transport_udp_session.open_session(address)
                dhnio.Dprint(8, 'transport_udp.doCreateNewUDPSession %s with [%s]' % (sess.name, nameurl.GetName(idurl)))
                sess.automat('init', idurl)
    
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
        address_local = self.remapAddress(address)
        for sess in transport_udp_session.sessions():
            if  sess.remote_idurl is not None and sess.remote_idurl == idurl and \
                ( sess.remote_address[0] == address[0] or sess.remote_address[0] == address_local[0] ) and \
                ( sess.remote_address[1] != address[1] or sess.remote_address[1] != address_local[1] ):
                dhnio.Dprint(8, 'transport_udp.doRestartUDPSession shutdown %s with [%s]' % (sess.name, nameurl.GetName(idurl)))
                sess.automat('shutdown')
        sess = transport_udp_session.open_session(address_local)
        dhnio.Dprint(8, 'transport_udp.doRestartUDPSession init %s with [%s]' % (sess.name, nameurl.GetName(idurl)))
        sess.automat('init', idurl)
         
    def doRecreateUDPSession(self, arg):
        def recreate(idurl, count):
            if count > 5:
                return
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
            if transport_udp_session.is_session_opened(address):
                reactor.callLater(1, recreate, idurl, count+1)
                dhnio.Dprint(8, 'transport_udp.doRecreateUDPSession.recreate wait 1 second to finish old session with %s' % str(address))
                return
            address_local = self.remapAddress(address)
#            if address != address_local and transport_udp_session.is_session_opened(address_local):
#                reactor.callLater(1, recreate, idurl, count+1)
#                dhnio.Dprint(6, 'transport_udp.doRecreateUDPSession.recreate wait 1 second to finish old local session with %s' % str(address_local))
#                return
            sess = transport_udp_session.open_session(address_local)
            dhnio.Dprint(8, 'transport_udp.doRecreateUDPSession init %s with [%s]' % (sess.name, nameurl.GetName(idurl)))
            sess.automat('init', idurl)
        reactor.callLater(random.randint(1, 10), recreate, arg, 0)
                        
    def doCloseDuplicatedUDPSession(self, arg):
        index, idurl = arg
        for sess in transport_udp_session.sessions():
            if sess.remote_idurl is not None and sess.remote_idurl == idurl and sess.index != index:
                dhnio.Dprint(8, 'transport_udp.doCloseDuplicatedUDPSession shutdown to %s with [%s]' % (sess.name, nameurl.GetName(idurl)))
                sess.automat('shutdown')
                        
    def doServerOutboxFile(self, arg):
        address = arg[0]
        filename, fast, description = arg[1]
        transport_udp_server.send(address, filename, fast, description)    
        
    def doClientOutboxFile(self, arg):
        address = arg[0]
        filename, fast, description = arg[1]
        address = self.remapAddress(address)
        if transport_udp_session.is_session_opened(address):
            transport_udp_session.outbox_file(address, filename, fast, description)
        else:
            dhnio.Dprint(2, 'transport_udp.doClientOutboxFile WARNIMG unknown address: ' + str(address))
            transport_udp_session.file_sent(address, filename, 'failed', 'udp', None, 'session not found')

    def doRequestRemoteID(self, arg):
        if isinstance(arg, str): 
            idurl = arg
            identitycache.immediatelyCaching(idurl).addCallbacks(
                lambda src: self.automat('remote-id-received', idurl),
                lambda x: self.automat('remote-id-failed', x))
        else:
            for idurl in arg[1]:
                if idurl == misc.getLocalID():
                    continue
                if idurl not in arg[0]:
                    identitycache.immediatelyCaching(idurl).addCallbacks(
                        lambda src: self.automat('remote-id-received', idurl),
                        lambda x: self.automat('remote-id-failed', x))

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
        _send_servers().addBoth(_id_sent)

    def _send_servers():
        import tmpfile, misc, nameurl, settings, transport_tcp
        sendfile, sendfilename = tmpfile.make("propagate")
        os.close(sendfile)
        LocalIdentity = misc.getLocalIdentity()
        dhnio.WriteFile(sendfilename, LocalIdentity.serialize())
        dlist = []
        for idurl in LocalIdentity.sources:
            # sources for out identity are servers we need to send to
            protocol, host, port, filename = nameurl.UrlParse(idurl)
            port = settings.IdentityServerPort()
            d = Deferred()
            transport_tcp.send(sendfilename, host, port, do_status_report=False, result_defer=d, description='Identity')
            dlist.append(d) 
        dl = DeferredList(dlist, consumeErrors=True)
        print '+++++ IDENTITY SENT TO', str(LocalIdentity.sources)
        return dl

    def _try2connect():
        remote_addr = dhnio.ReadTextFile(sys.argv[3]).split(' ')
        remote_addr = (remote_addr[0], int(remote_addr[1]))
        t = int(str(int(time.time()))[-1]) + 1
        data = '0' * t
        stun.getUDPClient().transport.write(data, remote_addr)
        print 'sent %d bytes to %s' % (len(data), str(remote_addr))
        reactor.callLater(1, _try2connect)

    def _id_sent(x):
        print '+++++ ID UPDATED ON THE SERVER', x
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
        _request_remote_id(idurl).addBoth(_send_to_remote_peer, idurl, sys.argv[3], None if len(sys.argv)<5 else int(sys.argv[4]))

    def _request_remote_id(idurl):
        print '+++++ REQUEST ID FROM SERVER', idurl
        return identitycache.immediatelyCaching(idurl)
    
    def _send_to_remote_peer(x, idurl, filename, loop_delay):
        print '+++++ PREPARE SENDING TO', idurl
        init(stun.getUDPClient())
        A().debug = True
        contacts.addCorrespondent(idurl)
        reactor.callLater(1, Start)
        if loop_delay:
            LoopingCall(_send_file, idurl, filename,).start(loop_delay, False)
        else:
            reactor.callLater(2, _send_file, idurl, filename,)
    
    def _send_file(idurl, filename):
        ident = identitycache.FromCache(idurl)
        if ident is None:
            print '+++++ REMOTE IDENTITY IS NONE'
            reactor.stop()
        x, udphost, udpport, x = ident.getProtoParts('udp')
        print '+++++ SENDING TO', udphost, udpport
        send(filename, udphost, udpport)
    
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
    if len(sys.argv) not in [2, 3, 4, 5, 6] or sys.argv[1] not in ['send', 'receive', 'listen', 'connect']:
        print 'transport_udp.py receive <from username>'
        print 'transport_udp.py receive <from idurl>'
        print 'transport_udp.py send <to username> <filename>'
        print 'transport_udp.py send <to idurl> <filename>'
        print 'transport_udp.py send <to username> <filename> <loop delay>'
        print 'transport_udp.py send <to idurl> <filename> <loop delay>'
        print 'transport_udp.py listen <listening port>'
        print 'transport_udp.py connect <listening port> <filename with remote address>'
        sys.exit(0)
        
    main()
    reactor.run()



