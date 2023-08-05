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


def start(AckHandler=None):
    dhnio.Dprint(6, "identitypropagate.start")
    d = Deferred()
    def fetch_done(x, d):
        dhnio.Dprint(6, "identitypropagate.start.fetch_done")
        SendToIDs(contacts.getRemoteContacts(), AckHandler)
        d.callback('sent')
        return x
    FetchAllContacts().addBoth(fetch_done, d)
    #update().addBoth(servers_done, d)
    return d


def suppliers(AckHandler=None):
    dhnio.Dprint(6, "identitypropagate.suppliers")
    FetchSuppliers().addBoth(lambda x: SendToIDs(contacts.getSupplierIDs(), AckHandler))


def customers(AckHandler=None):
    dhnio.Dprint(6, "identitypropagate.customers")
    FetchCustomers().addBoth(lambda x: SendToIDs(contacts.getCustomerIDs(), AckHandler))


def single(idurl, AckHandler=None):
    dhnio.Dprint(6, "identitypropagate.single " + idurl)
    FetchSingle(idurl).addBoth(lambda x: SendToIDs([idurl], AckHandler))
    

def update():
    dhnio.Dprint(6, "identitypropagate.update")
    return SendServers()


#def checkForIPChange(callback=None): # seems to take about a half second
#    dhnio.Dprint(4, "identitypropagate.checkForIPChange")
#    def _cb(ip):
#        if ip == '0.0.0.0':
#            return
#        AfterStun()
#        if callback:
#            callback()
#    updateIP(_cb)


#def updateIP(callback=None):
#    dhnio.Dprint(6, "identitypropagate.updateIP ")
#    d = stun.stunExternalIP()
#    d.addCallback(stunSuccess, callback)
#    d.addErrback(stunFailed, callback)


#def stunSuccess(ip, callback=None):
#    dhnio.Dprint(8, "identitypropagate.stunSuccess ")
#    dhnio.WriteFile(settings.ExternalIPFilename(), str(ip))         #  Save IP address in file
#    if callback:
#        callback(ip)


#def stunFailed(x, callback=None):
#    dhnio.Dprint(6, "identitypropagate.stunFailed NETERROR " + x.getErrorMessage())
#    if callback:
#        callback(None)


def UpdateLocalIdentity():
    nowip = misc.readExternalIP()
    dhnio.Dprint(6, "identitypropagate.UpdateLocalIdentity external ip=" + nowip)
    if nowip == '':
        dhnio.Dprint(1, "identitypropagate.UpdateLocalIdentity ERROR reading external ip")
        return False

    updated = False
    lid = misc.getLocalIdentity()
    for index in range(lid.getContactsNumber()):
        protocol, host, port, filename = lid.getContactParts(index)
        if protocol in ['tcp', 'ssh', 'http', ]:
            if host.strip() != nowip:
                lid.setContactParts(index, protocol, nowip, port, filename)
                updated = True

    if updated:
        misc.setLocalIdentity(lid)
        misc.saveLocalIdentity()

    return updated


def AfterStun():
    updated = UpdateLocalIdentity()

    if updated:
        #save our new identity to our identity servers
        SendServers()
        SendContacts()


def FetchSingle(idurl):
    dhnio.Dprint(8, "identitypropagate.FetchSingle " + idurl)
    return identitycache.scheduleForCaching(idurl)

def FetchAllContacts():
    dhnio.Dprint(8, "identitypropagate.FetchAllContacts ")
    dl = []
    for conID in contacts.getContactIDs():
        if conID.strip():
            dl.append(identitycache.scheduleForCaching(conID))
    return DeferredList(dl, consumeErrors=True)


def FetchSuppliers():
    dhnio.Dprint(8, "identitypropagate.FetchSuppliers")
    dl = []
    for idurl in contacts.getSupplierIDs():
        dl.append(identitycache.scheduleForCaching(idurl))
    return DeferredList(dl, consumeErrors=True)


def FetchCustomers():
    dhnio.Dprint(8, "identitypropagate.FetchCustomers")
    dl = []
    for idurl in contacts.getCustomerIDs():
        dl.append(identitycache.scheduleForCaching(idurl))
    return DeferredList(dl, consumeErrors=True)


def FetchNecesaryContacts():
    dhnio.Dprint(8, "identitypropagate.FetchNecesaryContacts ")
    dl = []
    for url in contacts.getContactIDs():
        if not identitycache.FromCache(url):
            dl.append(identitycache.scheduleForCaching(url))
    return DeferredList(dl, consumeErrors=True)


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
        dlist.append(transport_tcp.send(sendfilename, host, port, False))
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
    alreadysent=[]
    for contact in idlist:
        if contact.strip() == '':
            continue
        packet = dhnpacket.dhnpacket(
            commands.Identity(),
            misc.getLocalID(), #MyID,
            misc.getLocalID(), #MyID,
            misc.getLocalID(), #PacketID,
            Payload,
            contact)
        if contact not in alreadysent:
            # just want to send once even if both customer and supplier
            dhnio.Dprint(8, "identitypropagate.SendToIDs sending to " + contact)
            if AckHandler is not None:
                transport_control.RegisterInterest(AckHandler, packet.RemoteID, packet.PacketID)
            transport_control.outboxNoAck(packet)
            alreadysent.append(contact)
        else:
            dhnio.Dprint(8, "identitypropagate.SendToIDs already sent to " + contact)
    del alreadysent


def PingContact(idurl):
    SendToID(idurl, NeedAck=True)


