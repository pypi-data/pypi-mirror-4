#!/usr/bin/python
#contacts_status.py
#
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2012
#    Use of this software constitutes acceptance of the Terms of Use
#      http://datahaven.net/terms_of_use.html
#    All rights reserved.
#

import os
import sys

try:
    from twisted.internet import reactor
except:
    sys.exit('Error initializing twisted.internet.reactor in contacts_status.py')
    

import lib.dhnio as dhnio
import lib.nameurl as nameurl
import lib.transport_control as transport_control
import lib.contacts as contacts

import lib.automat as automat
#import lib.automats as automats

if transport_control._TransportCSpaceEnable:
    import lib.transport_cspace as transport_cspace


import ratings
#import customerservice


_ContactsByHost = {}
_ContactsStatusDict = {}


#------------------------------------------------------------------------------ 


def init():
    dhnio.Dprint(4, 'contacts_status.init')
    transport_control.AddInboxCallback(Inbox)
    transport_control.AddOutboxCallback(Outbox)
    transport_control.AddOutboxPacketStatusFunc(OutboxStatus)
    if transport_control._TransportCSpaceEnable:
        transport_cspace.SetContactStatusNotifyFunc(CSpaceContactStatus)


def shutdown():
    dhnio.Dprint(4, 'contacts_status.shutdown')
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
        automat.Automat.__init__(self, name, state, debug_level)
        
    def A(self, event, arg):
        #---CONNECTED---
        if self.state == 'CONNECTED':
            if event in [ 'send-failed', 'cspace-offline' ]: 
                self.state = 'OFFLINE'
            elif event == 'check':
                self.state = 'CHECKING'
            elif event == 'sent-timeout':
                self.doPingContact()
                self.state = 'CHECKING'
        #---OFFLINE---
        elif self.state == 'OFFLINE':
            if event == 'inbox-packet':
                self.state = 'CONNECTED'
            elif event in [ 'outbox-packet', 'check' ]:
                self.state = 'CHECKING'
        #---CHECKING---
        elif self.state == 'CHECKING':
            if event == 'inbox-packet':
                self.state = 'CONNECTED'
            elif event in [ 'send-failed', 'cspace-offline' ]:
                self.state = 'OFFLINE'

    def doPingContact(self):
        reactor.callLater(0, transport_control.PingContact, self.idurl)


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


def CSpaceContactStatus(keyID, status):
    global _ContactsByHost
    idurl = _ContactsByHost.get('cspace://' + keyID, None)
    if idurl is not None:
        A(idurl, 'cspace-'+status, keyID)


def PacketSendingTimeout(remoteID, packetID):
    dhnio.Dprint(6, 'contacts_status.PacketSendingTimeout ' + remoteID)
    A(remoteID, 'sent-timeout', packetID)

    

