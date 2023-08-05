#!/usr/bin/python
#identitypropagate.py
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2012
#    Use of this software constitutes acceptance of the Terms of Use
#      http://datahaven.net/terms_of_use.html
#    All rights reserved.
#
#
# When a user starts up he needs to run the stun.py to check what his IP is,
#  and if it has changed he needs to generate a new identity and send it to
#  his identityserver and all of his contacts.
#
# We also just request new copies of all identities from their servers when
#   we start up.   This is simple and effective.
#
# We should try contacting each contact every hour and if we have not been
# able to contact them in 2 or 3 hours then fetch copy of identity from
# their server.   PREPRO


import os
import sys


try:
    from twisted.internet import reactor
except:
    sys.exit('Error initializing twisted.internet.reactor in identitypropagate.py')


from twisted.internet.defer import DeferredList, Deferred


import lib.dhnio as dhnio
import lib.misc as misc
import lib.nameurl as nameurl
import lib.dhnpacket as dhnpacket
import lib.identitycache as identitycache
import lib.contacts as contacts
import lib.commands as commands
import lib.settings as settings
import lib.stun as stun
import lib.tmpfile as tmpfile
import lib.transport_control as transport_control
import lib.transport_tcp as transport_tcp


_SlowSendIsWorking = False

#------------------------------------------------------------------------------


def init():
    dhnio.Dprint(4, "identitypropagate.init ")
    transport_control.SetPingContactFunc(PingContact)


def propagate(selected_contacts, AckHandler=None):
    dhnio.Dprint(6, "identitypropagate.propagate to %d contacts" % len(selected_contacts))
    d = Deferred()
    def contacts_fetched(x, d, selected_contacts):
        dhnio.Dprint(6, "identitypropagate.propagate.contacts_fetched")
        SendToIDs(selected_contacts, AckHandler)
        d.callback('sent')
        return x
    fetch(selected_contacts).addBoth(contacts_fetched, d, selected_contacts)
    return d


def fetch(list_ids): 
    dhnio.Dprint(6, "identitypropagate.fetch identities for %d users" % len(list_ids))
    dl = []
    for url in list_ids:
        if not identitycache.FromCache(url):
            dl.append(identitycache.scheduleForCaching(url))
    return DeferredList(dl, consumeErrors=True)


def start(AckHandler=None):
    return propagate(contacts.getRemoteContacts(), AckHandler)


def suppliers(AckHandler=None):
    return propagate(contacts.getSupplierIDs(), AckHandler)


def customers(AckHandler=None):
    return propagate(contacts.getCustomerIDs(), AckHandler)


def single(idurl, AckHandler=None):
    FetchSingle(idurl).addBoth(lambda x: SendToIDs([idurl], AckHandler))
    

def update():
    dhnio.Dprint(6, "identitypropagate.update")
    return SendServers()


def FetchSingle(idurl):
    dhnio.Dprint(6, "identitypropagate.fetch_single " + idurl)
    return identitycache.scheduleForCaching(idurl)


def Fetch(idslist):
    return fetch(idslist)


def FetchSuppliers():
    return fetch(contacts.getSupplierIDs())


def FetchCustomers():
    return fetch(contacts.getCustomerIDs())


def FetchNecesaryContacts():
    return fetch(contacts.getContactIDs())
def FetchAllContacts(): 
    return fetch(contacts.getContactIDs())


def SendServers():
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
        transport_tcp.send(sendfilename, host, port, do_status_report=False, result_defer=d)
        dlist.append(d) 
        
    dl = DeferredList(dlist, consumeErrors=True)
    return dl


def SendSingleSupplier(idurl, response_callback=None):
    dhnio.Dprint(6, "identitypropagate.SendSingleSupplier [%s]" % nameurl.GetName(idurl))
    MyID = misc.getLocalID()
    packet = dhnpacket.dhnpacket(commands.Identity(), MyID, MyID, MyID, misc.getLocalIdentity().serialize(), idurl)
    transport_control.outboxNoAck(packet)
    if response_callback is not None:
        transport_control.RegisterInterest(response_callback, packet.RemoteID, packet.PacketID)


def SendSingleCustomer(idurl, response_callback=None):
    dhnio.Dprint(6, "identitypropagate.SendSingleCustomer [%s]" % nameurl.GetName(idurl))
    MyID = misc.getLocalID()
    packet = dhnpacket.dhnpacket(commands.Identity(), MyID, MyID, MyID, misc.getLocalIdentity().serialize(), idurl)
    transport_control.outboxNoAck(packet)
    if response_callback is not None:
        transport_control.RegisterInterest(response_callback, packet.RemoteID, packet.PacketID)


def SendContacts():
    dhnio.Dprint(6, "identitypropagate.SendContacts")
    SendToIDs(contacts.getContactIDs(), HandleAck)


def SendSuppliers():
    dhnio.Dprint(6, "identitypropagate.SendSuppliers")
#    guistatus.InitCallSuppliers()
    RealSendSuppliers()


def RealSendSuppliers():
    dhnio.Dprint(8, "identitypropagate.RealSendSuppliers")
    SendToIDs(contacts.getSupplierIDs(), HandleSuppliersAck)


def SlowSendSuppliers(delay=1):
    global _SlowSendIsWorking
    if _SlowSendIsWorking:
        dhnio.Dprint(8, "identitypropagate.SlowSendSuppliers  is working at the moment. skip.")
        return
    dhnio.Dprint(8, "identitypropagate.SlowSendSuppliers delay=%s" % str(delay))

    def _send(index, payload, delay):
        global _SlowSendIsWorking
        idurl = contacts.getSupplierID(index)
        if not idurl:
            _SlowSendIsWorking = False
            return
        transport_control.ClearAliveTime(idurl)
        SendToID(idurl, Payload=payload)
        reactor.callLater(delay, _send, index+1, payload, delay)

    _SlowSendIsWorking = True
    payload = misc.getLocalIdentity().serialize()
    _send(0, payload, delay)


def SlowSendCustomers(delay=1):
    global _SlowSendIsWorking
    if _SlowSendIsWorking:
        dhnio.Dprint(8, "identitypropagate.SlowSendCustomers  slow send is working at the moment. skip.")
        return
    dhnio.Dprint(8, "identitypropagate.SlowSendCustomers delay=%s" % str(delay))

    def _send(index, payload, delay):
        global _SlowSendIsWorking
        idurl = contacts.getCustomerID(index)
        if not idurl:
            _SlowSendIsWorking = False
            return
        transport_control.ClearAliveTime(idurl)
        SendToID(idurl, Payload=payload)
        reactor.callLater(delay, _send, index+1, payload, delay)

    _SlowSendIsWorking = True
    payload = misc.getLocalIdentity().serialize()
    _send(0, payload, delay)


def SendCustomers():
    dhnio.Dprint(8, "identitypropagate.SendCustomers")
#    guistatus.InitCallCustomers()
    RealSendCustomers()


def RealSendCustomers():
    dhnio.Dprint(8, "identitypropagate.RealSendCustomers")
    SendToIDs(contacts.getCustomerIDs(), HandleCustomersAck)


def HandleSingleSupplier(ackpacket):
    Num = contacts.numberForSupplier(ackpacket.OwnerID)
#    guistatus.SetShortStatusAlive(ackpacket, Num, "suppliers")


def HandleSingleCustomer(ackpacket):
    Num = contacts.numberForCustomer(ackpacket.OwnerID)
#    guistatus.SetShortStatusAlive(ackpacket, Num, "customers")


def HandleAck(ackpacket):
    #Num = contacts.numberForContact(ackpacket.OwnerID)
    dhnio.Dprint(6, "identitypropagate.HandleAck " + nameurl.GetName(ackpacket.OwnerID))
#    guistatus.SetShortStatusAlive(ackpacket, Num, "contacts")


def HandleSuppliersAck(ackpacket):
    Num = contacts.numberForSupplier(ackpacket.OwnerID)
    dhnio.Dprint(8, "identitypropagate.HandleSupplierAck ")
#    guistatus.SetShortStatusAlive(ackpacket, Num, "suppliers")


def HandleCustomersAck(ackpacket):
    Num = contacts.numberForCustomer(ackpacket.OwnerID)
    dhnio.Dprint(8, "identitypropagate.HandleCustomerAck ")
#    guistatus.SetShortStatusAlive(ackpacket, Num, "customers")


def SendToID(idurl, AckHandler=None, Payload=None, NeedAck=False):
    dhnio.Dprint(8, "identitypropagate.SendToID [%s] NeedAck=%s" % (nameurl.GetName(idurl), str(NeedAck)))
    thePayload = Payload
    if thePayload is None:
        thePayload = misc.getLocalIdentity().serialize()
    packet = dhnpacket.dhnpacket(
        commands.Identity(),
        misc.getLocalID(), #MyID,
        misc.getLocalID(), #MyID,
        misc.getLocalID(), #PacketID,
        thePayload,
        idurl)
    if AckHandler is not None:
        transport_control.RegisterInterest(AckHandler, packet.RemoteID, packet.PacketID)
    transport_control.outbox(packet, NeedAck)


def SendToIDs(idlist, AckHandler=None):
    dhnio.Dprint(6, "identitypropagate.SendToIDs to %d users" % len(idlist))
    MyID = misc.getLocalID()
    PacketID = MyID
    LocalIdentity = misc.getLocalIdentity()
    Payload = LocalIdentity.serialize()
    alreadysent = set()
    for contact in idlist:
        if contact.strip() == '':
            continue
        if contact in alreadysent:
            # just want to send once even if both customer and supplier
            continue
        packet = dhnpacket.dhnpacket(
            commands.Identity(),
            misc.getLocalID(), #MyID,
            misc.getLocalID(), #MyID,
            misc.getLocalID(), #PacketID,
            Payload,
            contact)
        dhnio.Dprint(8, "identitypropagate.SendToIDs to " + contact)
        if AckHandler is not None:
            transport_control.RegisterInterest(AckHandler, packet.RemoteID, packet.PacketID)
        transport_control.outboxNoAck(packet)
        alreadysent.add(contact)
    del alreadysent


def PingContact(idurl):
    SendToID(idurl, NeedAck=True)


