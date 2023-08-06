#!/usr/bin/python
#contact_status.py
#
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2013
#    Use of this software constitutes acceptance of the Terms of Use
#      http://datahaven.net/terms_of_use.html
#    All rights reserved.
#

import os
import sys
import time

try:
    from twisted.internet import reactor
except:
    sys.exit('Error initializing twisted.internet.reactor in contact_status.py')
    

import lib.dhnio as dhnio
import lib.nameurl as nameurl
import lib.transport_control as transport_control
import lib.contacts as contacts
import lib.identitycache as identitycache
import lib.automat as automat
import lib.settings as settings

if transport_control._TransportCSpaceEnable:
    import lib.transport_cspace as transport_cspace
if transport_control._TransportUDPEnable:
    import lib.transport_udp_session as transport_udp_session    

import ratings


_ContactsByHost = {}
_ContactsStatusDict = {}


#------------------------------------------------------------------------------ 


def init():
    dhnio.Dprint(4, 'contact_status.init')
    transport_control.AddInboxCallback(Inbox)
    transport_control.AddOutboxCallback(Outbox)
    transport_control.AddOutboxPacketStatusFunc(OutboxStatus)
    if transport_control._TransportCSpaceEnable:
        transport_cspace.SetContactStatusNotifyFunc(CSpaceContactStatus)
    if transport_control._TransportUDPEnable:
        transport_udp_session.SetStateChangedCallbackFunc(TransportUDPSessionStateChanged)


def shutdown():
    dhnio.Dprint(4, 'contact_status.shutdown')
    global _ContactsStatusDict
    for A in _ContactsStatusDict.values():
        automat.clear_object(A.index)
    _ContactsStatusDict.clear()
    

def isOnline(idurl):
    return A(idurl).state == 'CONNECTED'


def isOffline(idurl):
    return A(idurl).state == 'OFFLINE'


def isChecking(idurl):
    return A(idurl).state == 'CHECKING'


def hasOfflineSuppliers():
    for idurl in contacts.getSupplierIDs():
        if isOffline(idurl):
            return True
    return False


def countOfflineAmong(idurls_list):
    num = 0
    for idurl in idurls_list:
        if isOffline(idurl):
            num += 1
    return num

def countOnlineAmong(idurls_list):
    num = 0
    for idurl in idurls_list:
        if isOnline(idurl):
            num += 1
    return num

#------------------------------------------------------------------------------ 

def check_contacts(contacts_list):
    for idurl in contacts_list:
        A(idurl, 'check') 


def A(idurl, event=None, arg=None):
    global _ContactsStatusDict
    if not _ContactsStatusDict.has_key(idurl):
        _ContactsStatusDict[idurl] = ContactStatus(idurl, 'status_%s' % nameurl.GetName(idurl), 'OFFLINE', 10)
    if event is not None:
        _ContactsStatusDict[idurl].automat(event, arg)
    return _ContactsStatusDict[idurl]
      

class ContactStatus(automat.Automat):
    def __init__(self, idurl, name, state, debug_level):
        self.idurl = idurl
        self.time_connected = None
        automat.Automat.__init__(self, name, state, debug_level)
        
    def A(self, event, arg):
        #---CONNECTED---
        if self.state is 'CONNECTED':
            if event == 'check' :
                self.state = 'CHECKING'
            elif event == 'sent-timeout' and self.isTimePassed(arg) :
                self.state = 'CHECKING'
                self.doPingContact(arg)
            elif ( ( event == 'transport_udp_session.state' and arg is 'PING' ) ) or event == 'sent-failed' :
                self.state = 'OFFLINE'
                self.doRepaint(arg)
        #---OFFLINE---
        elif self.state is 'OFFLINE':
            if ( event == 'outbox-packet' or event == 'check' ) and self.isUDPPeerConnected(arg) :
                self.state = 'CHECKING'
            elif event == 'inbox-packet' or ( ( event == 'transport_udp_session.state' and arg is 'CONNECTED' ) ) :
                self.state = 'CONNECTED'
                self.doRememberTime(arg)
                self.doRepaint(arg)
        #---CHECKING---
        elif self.state is 'CHECKING':
            if event == 'sent-failed' or ( ( event == 'transport_udp_session.state' and arg is 'PING' ) ) :
                self.state = 'OFFLINE'
                self.doRepaint(arg)
            elif event == 'inbox-packet' or ( ( event == 'transport_udp_session.state' and arg is 'CONNECTED' ) ) :
                self.state = 'CONNECTED'
                self.doRememberTime(arg)
                self.doRepaint(arg)

    def doPingContact(self, arg):
        reactor.callLater(0, transport_control.PingContact, self.idurl)

    def isTimePassed(self, arg):
        if self.time_connected:
            return time.time() - self.time_connected > 60 * 5
        return False 

    def isUDPPeerConnected(self, arg):
        if not transport_control._TransportUDPEnable:
            return True
        if not settings.enableUDP():
            return True
        ident = contacts.getContact(self.idurl)
        if ident is None:
            return False
        address = ident.getProtoContact('udp')
        if address is None:
            return True
        try:
            ip, port = address[6:].split(':')
            address = (ip, int(port))
        except:
            dhnio.DprintException()
            return True
        s = transport_udp_session.get_session(address)
        if s is not None:
            return s.state is 'CONNECTED'
        address_local = identitycache.RemapContactAddress(address)
        s = transport_udp_session.get_session(address_local)
        if s is not None:
            return s.state is 'CONNECTED'
        return False
        
    def doRememberTime(self, arg):
        self.time_connected = time.time()
        
    def doRepaint(self, arg):
        if transport_control.GetContactAliveStateNotifierFunc() is not None:
            transport_control.GetContactAliveStateNotifierFunc()(self.idurl)


def OutboxStatus(workitem, proto, host, status, error, message):
    global _ContactsByHost
    ident = contacts.getContact(workitem.remoteid)
    if ident is not None:
        for contact in ident.getContacts():
            _ContactsByHost[contact] = workitem.remoteid
    if status == 'finished':
        A(workitem.remoteid, 'sent-done', (workitem, proto, host))
    else:
        A(workitem.remoteid, 'send-failed', (workitem, proto, host))


def Inbox(newpacket, proto, host):
    global _ContactsByHost
    ident = contacts.getContact(newpacket.OwnerID)
    if ident is not None:
        for contact in ident.getContacts():
            _ContactsByHost[contact] = newpacket.OwnerID
    A(newpacket.OwnerID, 'inbox-packet', (newpacket, proto, host))
    ratings.remember_connected_time(newpacket.OwnerID)
    

def Outbox(outpacket):
    global _ContactsByHost
    ident = contacts.getContact(outpacket.RemoteID)
    if ident is not None:
        for contact in ident.getContacts():
            _ContactsByHost[contact] = outpacket.RemoteID
    A(outpacket.RemoteID, 'outbox-packet', outpacket)


def PacketSendingTimeout(remoteID, packetID):
    # dhnio.Dprint(6, 'contact_status.PacketSendingTimeout ' + remoteID)
    A(remoteID, 'sent-timeout', packetID)


def TransportUDPSessionStateChanged(automatindex, oldstate, newstate):
    global _ContactsStatusDict
#    if not _ContactsStatusDict.has_key(idurl):
#        return
    sess = automat.objects().get(automatindex, None)
    if sess is None:
        return
    idurl = sess.remote_idurl
    if idurl is None:
        return
    ident = contacts.getContact(idurl)
    if ident is None:
        return
    address = ident.getProtoContact('udp')
    if address is None:
        return True
    try:
        ip, port = address[6:].split(':')
        address = (ip, int(port))
    except:
        dhnio.DprintException()
        return True
    if sess.remote_address == address or sess.remote_address == identitycache.RemapContactAddress(address):
        A(idurl, 'transport_udp_session.state', newstate)

