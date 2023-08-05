#!/usr/bin/python
#transport_control.py
#
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2012
#    All rights reserved.
#
# outbox - going out to rest of world - have a packet object:
#   We keep trying methods listed for the identity we want to send to, till one gets an ACK.
#   The ACK might come back in a different way and that is fine.
#   We have a queue of packets to send for each contact, but only send one at a time each
#
# inbox - in from rest of world - input is a filename:
#   sort of the firewall point.  We try to stop garbage as much as possible.
#   We also want to keep track of recent bandwidth so others can decide which dhnpackets
#   would be easiest to get.
#
# The  transport_tcp.py  and transport_ssh.py modules are the essential ones.
# The email and q2q are not so trusted.
#
# On startup we have to start any transport receive protocols that are listed in our identity
#   on the right ports.
#
#  PREPRO - seems we are not removing temprorary files when we are done with them
#
# We can have a list of who wants what dhnpackets.
# In particular, we can have dhnblocks
# that say any packet with their number on it.



import os
import sys
import time
from time import gmtime, strftime


try:
    from twisted.internet import reactor
except:
    sys.exit('Error initializing twisted.internet.reactor in transport_control.py')

from twisted.internet.defer import Deferred,  DeferredList, succeed
from twisted.internet import task


import dhnpacket
import dhncrypto
import misc
import nameurl
import dhnio
import identitycache
import contacts
import commands
import settings
import delayeddelete
import bandwidth
import webtraffic
import tmpfile
import stun


_TransportUDPEnable = True
_TransportHTTPEnable = False
_TransportCSpaceEnable = False
_TransportEmailEnable = False
_TransportSkypeEnable = False
_TransportQ2QEnable = False
_TransportSSHEnable = False


#if dhnio.Linux():
#    _TransportQ2QEnable = False
#if dhnio.Linux():
#    _TransportSkypeEnable = False
#if dhnio.Mac():
#    _TransportSkypeEnable = False

import transport_tcp

if _TransportSSHEnable:
    import transport_ssh

if _TransportQ2QEnable:
    import transport_q2q

#if _TransportEmailEnable:
#    import transport_email

#if _TransportSkypeEnable:
#    import transport_skype

if _TransportHTTPEnable:
    import transport_http

if _TransportCSpaceEnable:
    import transport_cspace
    
if _TransportUDPEnable:
    import transport_udp

#------------------------------------------------------------------------------

#_TransportControlAutomat = None

_InitDone = False
_DoingShutdown = False
_ShutdownCount = 0
_ShutdownDeferred = None
_ProtocolsListeners = {}
_ProtocolsOptions = {}
_SupportedProtocols = set()
_ProcessSendQueueWorker = None
_StartingProtocolsSet = None
_TimeNextSend = 0
_SendingDelay = 0.01
_LastReceiveTime = time.time()

_SendQueue = []
_InterestedParties = {}

_ContactLastAliveTime = {}
_SentFailedCountDict = {}
_SendingSpeedDict = {}
_PingContactsDict = {}

_LogDebugLevel = 14
_LogFile = None
_LogSpecificProtocol = ''

_InboxPacketCallbacksList = []
_OutboxPacketCallbacksList = []
_InboxPacketStatusCallbacksList = []
_OutboxPacketStatusCallbacksList = []

_ContactAliveStateNotifierFunc = None
_MessageFunc = None
_SendFileFunc = None
_ProtocolStateNotifier = None
_PingContactFunc = None

#------------------------------------------------------------------------------

#def A(event=None, arg=None):
#    global _TransportControlAutomat
#    if _TransportControlAutomat is None:
#        _TransportControlAutomat = TransportControl('transport_control', 'OFF', 4)
#    if event is not None:
#        _TransportControlAutomat.automat(event, arg)
#    return _TransportControlAutomat
#
#class TransportControl(Automat):
#    def A(self, event, arg):
#        pass

# init is called on startup
# from dhninit.py or install.py
def init(init_callback=None, init_contacts=None):
    global _InitDone
    global _TransportEmailEnable
    global _TransportQ2QEnable
    global _TransportSkypeEnable
    global _StartingProtocolsSet

    dhnio.Dprint(4, 'transport_control.init')
    if _InitDone:
        dhnio.Dprint(4, 'transport_control.init already working.')
        if init_callback:
            reactor.callLater(0, init_callback)
        return

    if init_contacts is None:
        contactsDict = misc.getLocalIdentity().getContactsByProto()
    else:
        contactsDict = init_contacts

    _StartingProtocolsSet = set(contactsDict.keys())


    #--- TCP transport
    contact = contactsDict.get('tcp', None)
    if contact and settings.enableTCP():
        try:
            proto, host, port, filename = nameurl.UrlParse(contact)
            proto = proto.strip()
            port = misc.DigitsOnly(port)
            if port == "":
                port = settings.DefaultTCPPort()

            def _tcp_done(l, init_callback, host, port, filename):
                SetProtocolListener('tcp', l)
                SetProtocolOptions('tcp', (host, port, filename))
                SetProtocolSupport('tcp')
                ProtocolReady('tcp', init_callback)

            def _tcp_failed(x, init_callback):
                SetProtocolSupport('tcp', False)
                ProtocolReady('tcp', init_callback, False)

            d = transport_tcp.receive(int(port))
            d.addCallback(_tcp_done, init_callback, host, port, filename)
            d.addErrback(_tcp_failed, init_callback)

        except:
            SetProtocolSupport('tcp', False)
            ProtocolReady('tcp', init_callback, False)
            dhnio.Dprint(1, 'transport_control.init ERROR starting transport TCP')
            dhnio.DprintException()

    else:
        _StartingProtocolsSet.discard('tcp')
        SetProtocolSupport('tcp', False)
        ProtocolReady('tcp', init_callback, False)


    #--- UDP transport
    contact = contactsDict.get('udp', None)
    if contact and settings.enableUDP() and _TransportUDPEnable:
        def _start_udp(x):
            if x in ['', '0.0.0.0', None]:
                SetProtocolSupport('udp', False)
                ProtocolReady('udp', init_callback, False)
                return
            try:
                host = stun.getUDPClient().externalAddress[0]
                port = str(stun.getUDPClient().externalAddress[1])
                transport_udp.init(stun.getUDPClient())
                l = transport_udp.getListener()
                SetProtocolListener('udp', l)
                SetProtocolOptions('udp', (host, port, ''))
                SetProtocolSupport('udp')
                ProtocolReady('udp', init_callback)
            except:
                SetProtocolSupport('udp', False)
                ProtocolReady('udp', init_callback, False)
                dhnio.Dprint(1, 'transport_control.init ERROR starting transport UDP')
                dhnio.DprintException()
        if stun.getUDPClient() is None:
            stun.stunExternalIP(close_listener=False, internal_port=int(settings.getUDPPort())).addBoth(_start_udp)
        else:
            _start_udp('')
    else:
        SetProtocolSupport('udp', False)
        ProtocolReady('udp', init_callback, False)


    #--- SSH transport
    contact = contactsDict.get('ssh', None)
    if contact and settings.enableSSH() and _TransportSSHEnable:
        try:
#            contact = localIdentity.getProtoContact('ssh')
            proto, host, port, filename = nameurl.UrlParse(contact)
            proto = proto.strip()
            port = misc.DigitsOnly(port)
            if port=="":
                port = settings.DefaultSSHPort()

            transport_ssh.init()

            def _ssh_done(l, init_callback, host, port, filename):
                SetProtocolListener('ssh', l)
                SetProtocolOptions('ssh', (host, port, filename))
                SetProtocolSupport('ssh')
                ProtocolReady('ssh', init_callback)

            def _ssh_failed(x, init_callback):
                SetProtocolSupport('ssh', False)
                ProtocolReady('ssh', init_callback, False)

            d = transport_ssh.receive(int(port))
            d.addCallback(_ssh_done, init_callback, host, port, filename)
            d.addErrback(_ssh_failed, init_callback)

        except:
            SetProtocolSupport('ssh', False)
            ProtocolReady('ssh', init_callback, False)
            dhnio.Dprint(1, 'transport_control.init ERROR starting transport SSH')
            dhnio.DprintException()


    else:
        _StartingProtocolsSet.discard('ssh')
        SetProtocolSupport('ssh', False)
        ProtocolReady('ssh', init_callback, False)


    #--- Q2Q transport
    contact = contactsDict.get('q2q', None)
    if contact and _TransportQ2QEnable and settings.enableQ2Q():
        try:
            def _q2q_done(x, init_callback):
                l = transport_q2q.getListener()
                SetProtocolListener('q2q', l)
                SetProtocolOptions('q2q', (settings.getQ2Quserathost(), '', '', 'receiving'))
                SetProtocolSupport('q2q')
                ProtocolReady('q2q', init_callback)

            def _q2q_failed(x, init_callback):
                SetProtocolSupport('q2q', False)
                ProtocolReady('q2q', init_callback, False)

            d = transport_q2q.init()
            d.addCallback(_q2q_done, init_callback)
            d.addErrback(_q2q_failed, init_callback)

        except:
            SetProtocolSupport('q2q', False)
            ProtocolReady('q2q', init_callback, False)
            dhnio.Dprint(1, 'transport_control.init ERROR starting transport Q2Q')
            dhnio.DprintException()

    else:
        _StartingProtocolsSet.discard('q2q')
        SetProtocolSupport('q2q', False)
        ProtocolReady('q2q', init_callback, False)


    #--- HTTP transport
    contact = contactsDict.get('http', None)
    if contact and _TransportHTTPEnable and (settings.enableHTTP() or settings.enableHTTPServer()):
        try:
            proto, host, port, filename = nameurl.UrlParse(contact)
            proto = proto.strip()
            port = misc.DigitsOnly(port)
            if port=="":
                port = settings.DefaultHTTPPort()

            transport_http.init()

            if settings.enableHTTPServer():
                transport_http.start_http_server(int(port))

            l = None
            if settings.enableHTTP() and misc.getLocalID() not in [settings.CentralID(), settings.MoneyServerID()]:
                l = transport_http.receive()
            SetProtocolListener('http', l)

            SetProtocolOptions('http', (host, port, filename))
            SetProtocolSupport('http')
            ProtocolReady('http', init_callback)

        except:
            SetProtocolSupport('http', False)
            ProtocolReady('http', init_callback, False)
            dhnio.Dprint(1, 'transport_control.init ERROR starting transport HTTP')
            dhnio.DprintException()

    else:
        _StartingProtocolsSet.discard('http')
        SetProtocolSupport('http', False)
        ProtocolReady('http', init_callback, False)


    #--- CSpace transport
    contact = contactsDict.get('cspace', None)
    if contact and _TransportCSpaceEnable and settings.enableCSpace():
        try:
            def _cspace_done(x, init_callback):
                l = transport_cspace.getListener()
                SetProtocolListener('cspace', l)
                SetProtocolOptions('cspace', (settings.getCSpaceKeyID(), '', '', 'receiving'))
                SetProtocolSupport('cspace')
                ProtocolReady('cspace', init_callback)
                transport_cspace.SetReceiveStatusReportFunc(receiveStatusReport)
                transport_cspace.SetSendStatusReportFunc(sendStatusReport)

            def _cspace_failed(x, init_callback):
                SetProtocolSupport('cspace', False)
                ProtocolReady('cspace', init_callback, False)

            d = transport_cspace.init()
            d.addCallback(_cspace_done, init_callback)
            d.addErrback(_cspace_failed, init_callback)

        except:
            SetProtocolSupport('cspace', False)
            ProtocolReady('cspace', init_callback, False)
            dhnio.Dprint(1, 'transport_control.init ERROR starting transport CSpace')
            dhnio.DprintException()

    else:
        _StartingProtocolsSet.discard('cspace')
        SetProtocolSupport('cspace', False)
        ProtocolReady('cspace', init_callback, False)


    dhnio.Dprint(6, 'transport_control.init _StartingProtocolsSet=%s' % str(_StartingProtocolsSet))

    #We are done!
    _InitDone = True

#------------------------------------------------------------------------------

def AddInboxCallback(callback):
    global _InboxPacketCallbacksList
    if callback not in _InboxPacketCallbacksList:
        _InboxPacketCallbacksList.append(callback)

def AddOutboxCallback(callback):
    global _OutboxPacketCallbacksList
    if callback not in _OutboxPacketCallbacksList:
        _OutboxPacketCallbacksList.append(callback)

def AddInboxPacketStatusFunc(callback):
    global _InboxPacketStatusCallbacksList
    if callback not in _InboxPacketStatusCallbacksList:
        _InboxPacketStatusCallbacksList.append(callback)

def AddOutboxPacketStatusFunc(callback):
    global _OutboxPacketStatusCallbacksList
    if callback not in _OutboxPacketStatusCallbacksList:
        _OutboxPacketStatusCallbacksList.append(callback)

def SetProtocolStateNotifier(func):
    global _ProtocolStateNotifier
    _ProtocolStateNotifier = func

def SetMessageFunc(func):
    global _MessageFunc
    _MessageFunc = func

def SetContactAliveStateNotifierFunc(func):
    global _ContactAliveStateNotifierFunc
    _ContactAliveStateNotifierFunc = func

def SetPingContactFunc(func):
    global _PingContactFunc
    _PingContactFunc = func

def PingContact(idurl):
    global _PingContactFunc
    if _PingContactFunc is not None:
        _PingContactFunc(idurl)

def GetOutboxFunc():
    return outboxNoAck

def RemoveFileAfterSending():
    return True

def RemoveFileAfterReceiveing():
    return True

#-------------------------------------------------------------------------------

def ListSupportedProtocols():
    global _SupportedProtocols
    return list(_SupportedProtocols)

def ProtocolIsSupported(proto):
    global _SupportedProtocols
    return proto in _SupportedProtocols

def SetProtocolSupport(proto, state=True):
    global _SupportedProtocols
    global _ProtocolStateNotifier
    if state:
        _SupportedProtocols.add(proto)
    else:
        _SupportedProtocols.discard(proto)
    if _ProtocolStateNotifier is not None:
        _ProtocolStateNotifier(proto, state)

def ProtocolListener(proto):
    global _ProtocolsListeners
    return _ProtocolsListeners.get(proto, None)

def SetProtocolListener(proto, listener):
    global _ProtocolsListeners
    _ProtocolsListeners[proto] = listener

def ProtocolOptions(proto):
    global _ProtocolsOptions
    return _ProtocolsOptions.get(proto, None)

def SetProtocolOptions(proto, options_tuple):
    global _ProtocolsOptions
    _ProtocolsOptions[proto] = options_tuple

def StopProtocol(proto):
    dhnio.Dprint(4, 'transport_control.StopProtocol ' + proto)
    d = None
    l = ProtocolListener(proto)
    if l is not None:
        try:
            if proto == 'tcp':
                d = l.stopListening()
            elif proto == 'ssh':
                d = l.stopListening()
            elif proto == 'q2q':
                d = l.stopListening()
            elif proto == 'http':
                if l is not None:
                    if not l.called:
                        l.cancel()
            elif proto == 'cspace':
                if l is not None:
                    l.stopListening()
            elif proto == 'udp':
                if l is not None:
                    d = l.stopListening()
            else:
                dhnio.Dprint(1, 'transport_control.StopProtocol  ERROR not done YET!!!')
            del l
        except:
            dhnio.DprintException()
    SetProtocolListener(proto, None)
    SetProtocolOptions(proto, ('','','',''))
    SetProtocolSupport(proto, False)
    if d is None:
        d = Deferred()
        d.callback('')
    return d

def StartProtocol(proto, listener, host, port, filename, init_callback=None):
    dhnio.Dprint(6, 'transport_control.StartProtocol %s//:%s:%s' % (proto, host, str(port)))
    SetProtocolListener(proto, listener)
    SetProtocolOptions(proto, (host, port, filename))
    SetProtocolSupport(proto)
    ProtocolReady(proto, init_callback)

#-------------------------------------------------------------------------------

def CombineIDs(CreatorID, PacketID):
    return str(CreatorID) + ":" + str(PacketID)

class InterestedParty:
    def __init__(self, CallBackFunctionOrDefer, CreatorID, PacketID):
        dhnio.Dprint(12, "transport_control.InterestedParty making " + str(PacketID))
        # function(or Deferred)  to call when we see this packet
        self.CallBackFunction=CallBackFunctionOrDefer
        self.ComboID = CombineIDs(CreatorID, PacketID)

# cancel an interest
def RemoveInterest(CreatorID, PacketID):
    global _InterestedParties
    comboID = CombineIDs(CreatorID, PacketID)
    if _InterestedParties.has_key(comboID):
        dhnio.Dprint(12, "transport_control.RemoveInterest comboID=" + str(comboID))
        del _InterestedParties[comboID]

# Idea is to have a list for each ComboID so that there might be more than one place called, but unique entries in that list
def RegisterInterest(CallBackFunction, CreatorID, PacketID):
    global _InterestedParties
    newparty = InterestedParty(CallBackFunction, str(CreatorID), str(PacketID))
    ExistingList = _InterestedParties.get(newparty.ComboID, "")
    if len(ExistingList) > 0:
        for oldparty in ExistingList:
            if oldparty.CallBackFunction == CallBackFunction and oldparty.ComboID == newparty.ComboID:
                return                                # already here

    if len(ExistingList) == 0:                      # if nothing there
        _InterestedParties[newparty.ComboID]=[]        #    then make it a list

    _InterestedParties[newparty.ComboID].append(newparty) # add new callback to list

    lp=len(_InterestedParties)
    #dhnio.Dprint(12, "transport_control.RegisterInterest ComboID=%s _InterestedParties=%s " % (newparty.ComboID, str(lp)))


def FindInterestedParty(newpacket):
    global _InterestedParties
    lp = len(_InterestedParties)
    #dhnio.Dprint(12, "transport_control.FindInterestedParty  lenIP= " + str(lp))
    found = False
    ComboID = CombineIDs(newpacket.CreatorID, newpacket.PacketID)
    for party in _InterestedParties.get(ComboID, []):
        #dhnio.Dprint(12, "transport_control.FindinterestedParty Someone wants " + ComboID )
        # let him see the packet
        FuncOrDefer = party.CallBackFunction
        if isinstance(FuncOrDefer, Deferred):
            FuncOrDefer.callback(newpacket)
        else:
            FuncOrDefer(newpacket)
        found = True
    if _InterestedParties.has_key(ComboID):             # not everything has an interested party/callback
        del _InterestedParties[ComboID]                 # We called all interested parties, remove entry in dictionary
    return found


# We record interest in this packet and then send a request for it
# This is used by restore.py
def FetchAndCallBack(CallBackFunction, CreatorID, PacketID, SupplierNumber):
    RemoteID = contacts.getSupplierID(SupplierNumber)
    dhnio.Dprint(12, "transport_control.FetchAndCallBack with RemoteID =" + RemoteID)
    RegisterInterest(CallBackFunction, CreatorID, PacketID)
    newpacket = dhnpacket.dhnpacket(commands.Retrieve(), CreatorID, CreatorID, PacketID, "", RemoteID)
    outboxNoAck(newpacket)      # send request packet - PREPRO - check that Ack really works ok
    #outbox(newpacket)          # send request packet - PREPRO - check that Ack really works ok

# deal with removing any interest in any potential data file belonging to a backup we're deleting,
# we don't want to call something trying to rebuild a backup we're deleting
def DeleteBackupInterest(BackupName):
    global _InterestedParties
    found = False
    partystoremove=[]
    for combokey in _InterestedParties.keys():
        if (combokey.find(":"+BackupName) != -1): # if the interest is for packet belonging to a backup we're dealing with
            dhnio.Dprint(12, "transport_control.DeleteBackupInterest found for " + combokey)
            partystoremove.append(combokey)                   #   will remove party since got his callback
            found=True
    for combokey in partystoremove:                           #
        dhnio.Dprint(12, "transport_control.DeleteBackupInterest removing " + combokey)
        del _InterestedParties[combokey]
    del partystoremove
    return found

# status can be:
#     finished     - we think we sent/received it ok
#     progress X   - sent/received X bytes so far
#     failed       - did not work for some reason


def ProtocolReady(proto, init_callback=None, state=True):
    global _SupportedProtocols
    global _ProcessSendQueueWorker
    global _StartingProtocolsSet
    #we need protocols to be ready before we start sending packets.
    #here we need to decide when we are ready.
    #just to be simple now. if we have 3 working protocols we can start
    #TODO need to improve this in future
    #Veselin changed this today
    #if first contact of the local id is ready - we are ready
    #because everybody using our first contact to send us a packets
    #Veselin changed this today again :-)
    #We want to receive ALL packets from central server when we starts
    #central will reply to our first packet using ALL our contact methods
    #so we need to be sure that ALL our transports was started
    #before we will send this first packet to central server
    #disabled transport should be counted too.

    #if we are already started - exit
    if _ProcessSendQueueWorker is not None:
        return

    #if transport_control.init() is not called yet - exit
    if _StartingProtocolsSet is None:
        return

    _StartingProtocolsSet.discard(proto)

    dhnio.Dprint(4, 'transport_control.ProtocolReady: %s with state=%s others: %s' % (str(proto), str(state), str(_StartingProtocolsSet)))

    #if all transports started - we are done
    if len(_StartingProtocolsSet) == 0:
        dhnio.Dprint(2, 'transport_control.ProtocolReady DECIDES TO START SENDING PACKETS !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        #init gets this started then ProcessSendQueue keeps adding self with callLater
        StartSendQueue()

        if init_callback is not None:
            reactor.callLater(0, init_callback)


def StartSendQueue():
    global _ProcessSendQueueWorker
    dhnio.Dprint(4, 'transport_control.StartSendQueue')
    if _ProcessSendQueueWorker is not None:
        dhnio.Dprint(6, 'transport_control.StartSendQueue already started')
        return
#    _ProcessSendQueueWorker = task.LoopingCall(ProcessSendQueue)
#    _ProcessSendQueueWorker.start(0.05)
    _ProcessSendQueueWorker = reactor.callLater(0, ProcessSendQueue)


def stillActive():
    result = stillSending() or TimeSinceLastReceive < 60
    #dhnio.Dprint(14, "transport_control.stillActive " + str(result))
    return result

# PREPRO really should have a callback
# that polls to see if receiving is done also
# and does callback after
# both sending and receiving is finished.
def stillSending():
    result = SendQueueLength() > 0
    #dhnio.Dprint(14, "transport_control SendQueueLength=" + str(SendQueueLength()))
    #dhnio.Dprint(12, "transport_control.stillSending returning " + str(result))
    return result

def TimeSinceLastReceive():
    global _LastReceiveTime
    now = time.time()
    delta = now - _LastReceiveTime
    return delta

#------------------------------------------------------------------------------
# 1) The protocol modules write to temporary files and gives us that filename
# 2) We unserialize
# 3) We check that it is for us
# 4) We check that it is from one of our contacts.
# 5) We use dhnpacket.validate() to check signature and that number fields are numbers
# 6) Any other sanity checks we can do and if anything funny we toss out the packet.
# 7) Then change the filename to the dhnpacket.PackedID that it should be.
#     and call the right function(s) for this new dhnpacket
#     (dhnblock, scrubber, remotetester, customerservice, ...)
#     to dispatch it to right place(s).
#
# We have to keep track of bandwidth to/from everyone, and make a report every 24 hours
# which we send to DHN sometime in the 24 hours after that.
def inbox(filename, proto='', host=''):
    global _InboxPacketCallbacksList
    global _DoingShutdown

    if _DoingShutdown:
        dhnio.Dprint(6, "transport_control.inbox ignoring input since _DoingShutdown ")
        return None

    if filename == "" or not os.path.exists(filename):
        dhnio.Dprint(1, "transport_control.inbox  ERROR bad filename=" + filename)
        return None

    try:
        data = dhnio.ReadBinaryFile(filename)
    except:
        dhnio.Dprint(1, "transport_control.inbox ERROR reading file " + filename)
        return None

    if len(data) == 0:
        dhnio.Dprint(1, "transport_control.inbox ERROR zero byte file from %s://%s" % (proto, host))
        return None

    try:
        newpacket = dhnpacket.Unserialize(data)
    except:
        dhnio.Dprint(1, "transport_control.inbox ERROR during Unserialize data from %s://%s" % (proto, host))
        dhnio.DprintException()
        return None

    try:
        Command = newpacket.Command
        OwnerID = newpacket.OwnerID
        CreatorID = newpacket.CreatorID
        PacketID = newpacket.PacketID
        Date = newpacket.Date
        Payload = newpacket.Payload
        RemoteID = newpacket.RemoteID
        Signature = newpacket.Signature
        if OwnerID == misc.getLocalID() and Command == commands.Data():
            OwnerID = RemoteID
        packet_sz = len(data)
        dhnio.Dprint(12, "transport_control.inbox [%s] from %s" % (Command , OwnerID))
    except:
        dhnio.Dprint(1, "transport_control.inbox ERROR during Unserialize data from %s://%s" % (proto, host))
        dhnio.Dprint(1, "data length=" + str(len(data)))
        dhnio.DprintException()
        fd, filename = tmpfile.make('other', '.bad')
        os.write(fd, data)
        os.close(fd)
        return None

    UpdateContactAliveTime(OwnerID)
    #contact_status(packet_from, 'inbox-packet', newpacket)

    # Might be someone who wants to look at this - remember if found someone
    foundInterest = FindInterestedParty(newpacket)

#    if newpacket.Command == commands.Ack():
#        FindAckWaitingPacket(newpacket)

    packetHandled = False
    for cb in _InboxPacketCallbacksList:
        try:
            if cb(newpacket, proto, host):
                packetHandled = True
        except:
#            # Can't get too excited about it though
            dhnio.Dprint(1, 'transport_control.inbox ERROR in callback from _InboxPacketCallbacksList: ' + str(cb))
            dhnio.DprintException()

    if not packetHandled and not foundInterest:
        dhnio.Dprint(1, "transport_control.inbox ERROR have unhandled packet [%s] %s " % (Command, PacketID))

    return newpacket


def SendAck(packettoack, response=''):
    MyID = misc.getLocalID()
    RemoteID = packettoack.OwnerID
    PacketID = packettoack.PacketID
    dhnio.Dprint(14, "transport_control.SendAck sending to " + RemoteID)
    result = dhnpacket.dhnpacket(commands.Ack(),  MyID, MyID, PacketID, response, RemoteID)
    outboxNoAck(result)
##    dhnpacket.MakePacketInThread(outboxNoAck, commands.Ack(), MyID, MyID, PacketID, response, RemoteID)


# We can have a bunch of different "DHNPackets" that need to
# get to different IDURLs in various stages of getting out.
# The total amount of things is sort of like a window-size in
# TCP, tells you how many packets can be outstanding at once.
# Probably the idea it to keep it something that fits in RAM.
# So maybe 200 DHNPackets of 1 MB each, or something like that.
# For example, as we generate the ZIP we could do next 116 (64+52)
# DHNPackets after we got down to 84 unfinished DHNPackets.
#
# For each "DHNPackets" and an IDURL to send to,
# transport-control will work down the list of contact methods for that IRURL
# asking outbox to send by each method till we get ACK back.
# If the first is ssh we then use transport-ssh.py to send it
# (passing both DHNPackets and IDURL to that), and if email
# then we use an email-send.py, if vertex then vertex-send.py, etc.
#
# For some of these the send-*.py can get an ACK and know the
# DHNPackets got through.
#
# Point of this is to have one small file that is all someone needs
# to look at to add a new way to send DHNPackets
def outboxAck(outpacket, wide=False):
    # True = Should keep record of packet and retry till ACK comes back  -
    outbox(outpacket, True, wide)

def outboxNoAck(outpacket, wide=False):
    # False = control is not responsible for retries
    outbox(outpacket, False, wide)

def outboxAfterIdentityCaching(pagesrc, outpacket, doAck, wide=False):
    dhnio.Dprint(12, 'transport_control.outboxAfterIdentityCaching')
    outbox(outpacket, doAck, wide)

# need to dealt with this situation
# this may happening if identity.datahaven.net is not responding
def identityCachingFailed(pagesrc, destinationID, outpacket, doAck, wide=False, count=0):
    dhnio.Dprint(6, 'transport_control.identityCachingFailed for %s NETERROR, count=%d' % (destinationID, count))
    def do_again(count):
        if count >= 3:
            return
        d = identitycache.immediatelyCaching(destinationID)
        d.addCallback(outboxAfterIdentityCaching, outpacket, doAck, wide)
        d.addErrback(identityCachingFailed, destinationID, outpacket, doAck, wide, count)
    reactor.callLater(10, do_again, count+1)

# doAck=True      if we want to wait for an Ack before counting finished
# wide=True       if we want to send packet to all contacts of Remote Identity
# retries=3       how mamy times we want to try to send the packet
def outbox(outpacket, doAck, wide=False, retries=settings.MaxRetries()):
    global _OutboxPacketCallbacksList
    global _PingContactsDict

    if not outpacket.Ready():
        outpacket.SigningDefer.addCallback(outbox, doAck)
        return

    if outpacket.CreatorID != misc.getLocalID():      # if we did not make this packet
        if outpacket.Command == commands.Data():      #  and it is a Data packet
            destinationID = outpacket.CreatorID       #  sending someone their data back
        else:
            raise Exception("transport_control.outbox has packet we did not make that is not Data packet")
    else:
        # we made packet for someone else
        destinationID = outpacket.RemoteID

    destinationID = destinationID.strip()

    if destinationID == '':
        return

    dhnio.Dprint(12, "transport_control.outbox [%s] to %s doAck=%s wide=%s" % (outpacket.Command, outpacket.RemoteID, str(doAck), str(wide)))
    for cb in _OutboxPacketCallbacksList:
        try:
            cb(outpacket)
        except:
            dhnio.Dprint(1, "transport_control.ProcessSendQueue ERROR exception in callback of _OutboxPacketCallbacksList:")
            dhnio.DprintException()

    fileno, filename = tmpfile.make('outbox')
    packet_data = outpacket.Serialize()
    os.write(fileno, packet_data)
    os.close(fileno)

    #  convert ID to identity
    destinationIdentity = contacts.getContact(destinationID)
    if destinationIdentity is None:
        d = identitycache.immediatelyCaching(destinationID)
        d.addCallback(outboxAfterIdentityCaching, outpacket, doAck, wide)
        d.addErrback(identityCachingFailed, destinationID, outpacket, doAck, wide, 0)
        # Can not send without identity
        return

    workitem = QueueItem(
        filename,
        len(packet_data),
        doAck,
        "presend",
        outpacket.PacketID,
        destinationID,
        outpacket.Command,
        wide,
        len(outpacket.Payload),
        retries,)
    SendQueueAppend(workitem)

    _PingContactsDict[destinationID] = time.time()
    
    del packet_data

    #contact_status(destinationID, 'outbox-packet', outpacket)

    dhnio.Dprint(14, "transport_control.outbox queue=%d" % SendQueueLength())


#------------------------------------------------------------------------------
# If it has stopped for a long time we might kill transfer.
# If the file is over the legal limit, we should kill transfer.
def receiveStatusReport(filename, status, proto='', host_=None, error=None, message=''):
    global _InitDone
    global _LastReceiveTime
    global _InboxPacketStatusCallbacksList
    _LastReceiveTime = time.time()

    host = host_
    if isinstance(host, str):
        if host.startswith('http://'):
            host = host[7:]
    elif isinstance(host, tuple) and len(host) == 2:
        host = host[0] + ':' + str(host[1])
    elif host is None:
        host = 'unknown'
    else:
        if getattr(host, 'host', None) is not None:
            if getattr(host, 'port', None) is not None:
                host = str(getattr(host, 'host')) + ':' + str(getattr(host, 'port'))
            else:
                host = str(getattr(host, 'host'))
        elif getattr(host, 'underlying', None) is not None:
            host = str(getattr(host, 'underlying'))

    msg = message
    if error is not None:
        if proto != 'tcp':
            msg = '(' + str(error) + ') ' + msg

    dhnio.Dprint(8, '            [%s] {IN}  %s from %s %s %s' % (proto.upper(), status.ljust(8), host, msg, os.path.basename(filename),))

    if not _InitDone:
        return

    newpacket = inbox(filename, proto, host)

    if newpacket is not None:
        for cb in _InboxPacketStatusCallbacksList:
            cb(newpacket, status, proto, host, error, message)

        if settings.enableWebTraffic():
            webtraffic.inbox(newpacket, proto, host, status)

        bandwidth.INfile(filename, newpacket, proto, host, status)

    else:
        try:
            fd, filename = tmpfile.make('other', '.inbox.error')
            data = dhnio.ReadBinaryFile(filename)
            os.write(fd, 'from %s:%s %s\n' % (proto, host, status))
            os.write(fd, str(data))
            os.close(fd)
        except:
            dhnio.DprintException()

    if RemoveFileAfterReceiveing():
        #delayeddelete.DeleteAfterTime(filename, 60)
        tmpfile.throw_out(filename)




#------------------------------------------------------------------------------
# When the transport layer has finished or failed
# it calls this so we can clean up queue and temp file
# Tricky problem is when we are doing a retransmission
# (sending same again) and get Ack from first time.
def sendStatusReport(host_, filename, status, proto='', error=None, message=''):
    global _InitDone
    global _SendQueue
    global _OutboxPacketStatusCallbacksList
    global _SentFailedCountDict
    global _SendingSpeedDict

    host = misc.getRealHost(host_)

    msg = message
    if error is not None:
        if proto != 'tcp':
            msg = '(' + str(error) + ') ' + msg

    if not _InitDone:
        return

    speed = 0
    itemstoremove=[]
    for workitem in _SendQueue:
        if filename == workitem.filename:
            workitem.counts -= 1
            # If we don't need an Ack or already have it then we are done with this
            if workitem.doack == False or workitem.status == "acked":
                itemstoremove.append(workitem)
            else:
                workitem.status = "sent"

            if workitem.started is not None and status == 'finished':
                speed = float(workitem.filesize) / (time.time() - workitem.started + 0.01)
                _SendingSpeedDict[workitem.remoteid] = speed
                #dhnio.Dprint(14, "transport_control.sendStatusReport %d kb/s" % int(speed/1024))

            if not _SentFailedCountDict.has_key(workitem.remoteid):
                _SentFailedCountDict[workitem.remoteid] = 0

            if status == 'finished':
                _SentFailedCountDict[workitem.remoteid] = 0
            else:
                _SentFailedCountDict[workitem.remoteid] += 1
                #dhnio.Dprint(14, "transport_control.sendStatusReport _SentFailedCountDict[%s]=%d" % (workitem.remoteid, _SentFailedCountDict[workitem.remoteid]))

            #contact_status(workitem.remoteid, 'sent-status-report', (workitem, proto, host, status))

            for cb in _OutboxPacketStatusCallbacksList:
                cb(workitem, proto, host, status, error, message)

            if settings.enableWebTraffic():
                webtraffic.outbox(workitem, proto, host, status)

            bandwidth.OUTfile(filename, workitem, proto, host, status)

    # Also removes filename
    for itemtoremove in itemstoremove:
        SendQueueRemove(itemtoremove, True)
    del itemstoremove

    dhnio.Dprint(8, "            [%s] (OUT) %s to %s %s %s at %d kb/s" % (proto.upper(), status.ljust(8), host, msg, os.path.basename(filename), int(speed/1024)))

#------------------------------------------------------------------------------


class QueueItem:
    def __init__(self,
            filename,
            filesize,
            doack,
            status,
            packetid,
            remoteid,
            command,
            wide,
            payloadsize,
            retries = settings.MaxRetries(),
            ):
        self.filename = filename
        self.filesize = filesize
        self.payloadsize = payloadsize
        self.doack = doack
        #"presend" - not started yet
        #"sending" - transport working on it
        #"sent" - transport says finished
        #"acked" - have ack
        self.status = status
        self.packetid = packetid
        self.remoteid = remoteid
        self.command = command
        self.wide = wide
        self.time = time.time()
        self.started = None
        self.timeout = settings.SendTimeOut()
        #self.retries = 0
        self.retries = retries
        if self.command in [ commands.Data(), ]:
            self.retries = 1
        self.counts = 0


#------------------------------------------------------------------------------
# we want to know who are still alive

def GetContactAliveTime(idurl):
    global _ContactLastAliveTime
    return _ContactLastAliveTime.get(idurl, 0)

def TestAlive(alive_time, period=settings.DefaultAlivePacketTimeOut()*2):
    return time.time() - alive_time < period

def UpdateContactAliveTime(idurl):
    global _ContactLastAliveTime
    global _ContactAliveStateNotifierFunc
    global _SentFailedCountDict

    # we need to fire event - the contact is alive now
    # so we have to check did he was offile before
    if not TestAlive(GetContactAliveTime(idurl)):
        if _ContactAliveStateNotifierFunc is not None:
            _ContactAliveStateNotifierFunc(idurl)

    _ContactLastAliveTime[idurl] = time.time()
    _SentFailedCountDict[idurl] = 0



#------------------------------------------------------------------------------
# This is very important method
# We really need to know who is ready at the moment
# Some aspects to decide if contact is online or not:
# 1. Did not get packets from him for a long tim = offline
# 2. sendStatusReport is failed = offline
# 3. transport_cspace is tracking users - we can use it to decide
#    if user do not have cspace contact - this not fit.
#    but most users will have it!
# 4. if we check to offten - this no good, give more traffic
# 5. if we check to rarely - we have wrong info


def ContactIsAlive(idurl):
    global _SentFailedCountDict
    global _PingContactFunc
    global _PingContactsDict

    # if we haven't gotten a packet from the contact,
    # make an entry so we can have some idea
    # how long we haven't heard from him
    if GetContactAliveTime(idurl) == 0:
        ClearAliveTime(idurl)

    # if we are trying to send some packets to him
    # but it was failed - we decide that he is offline
    if _SentFailedCountDict.has_key(idurl) and _SentFailedCountDict[idurl] >= 1:
        ClearAliveTime(idurl)
        _SentFailedCountDict[idurl] = 0

    # if we did not checked this man for 15 minutes - let's do it
    # but not too often - let's check when we did it last time
    # but if this is the Central server machine - we should not do it
    if _PingContactFunc is not None:
        if misc.getLocalID() not in [settings.CentralID(), settings.MoneyServerID()]:
            ping_preiod = settings.DefaultAlivePacketTimeOut() / 4
            if TestAlive(GetContactAliveTime(idurl), ping_preiod):
                if time.time()-_PingContactsDict.get(idurl, time.time()-100*ping_preiod) > ping_preiod:
                    dhnio.Dprint(8, 'transport_control.ContactIsAlive want to ping [%s]' % nameurl.GetName(idurl))
                    reactor.callLater(0, _PingContactFunc, idurl)
                    # we do update _PingContactsDict
                    # in the transport_control.outbox
                    # _PingContactsDict[idurl] = time.time()

    # check if we have some packets from contact in last hours
    return TestAlive(GetContactAliveTime(idurl))

#------------------------------------------------------------------------------


def ClearAliveTime(idurl):
    global _ContactLastAliveTime
    _ContactLastAliveTime[idurl] = time.time() - settings.DefaultAlivePacketTimeOut() * 100

def ClearAliveTimeAllContacts():
    global _ContactLastAliveTime
    for idurl in _ContactLastAliveTime.keys():
        ClearAliveTime(idurl)

def ClearAliveTimeSuppliers():
    global _ContactLastAliveTime
    for idurl in contacts.getSupplierIDs():
        ClearAliveTime(idurl)

def ClearAliveTimeCustomers():
    global _ContactLastAliveTime
    for idurl in contacts.getCustomerIDs():
        ClearAliveTime(idurl)

def SendingSpeed(idurl):
    global _SendingSpeedDict
    return _SendingSpeedDict.get(idurl, 0)

#def GetSuppliersOnlineCount():
#    n = 0
#    for idurl in contacts.getSupplierIDs():
#        if ContactIsAlive(idurl):
#            n += 1
#    return n

#------------------------------------------------------------------------------
# Only count stuff for Active nodes - don't want to count nodes that are not answering now
# Could keep track of we have sent to but not gotten an answer from in 15 minutes or something
# Need to be careful that just loosing a packet does not qualify as being down.
# Also, if we have not sent them anything then can't complain if they don't send us anything
# So maybe keep track of last send and last receive, and "down
# Mostly want this for when doing a backup, so could just clear things at start of backup.
# Really want to know how many Data packets are waiting for sites that are Active.
def SendQueueActiveDataLength():
    global _SendQueue
##    dhnio.Dprint(14, "transport_control.SendQueueActiveDataLength")
    datacount=0
    for workitem in _SendQueue:
        if (workitem.command == commands.Data() and ContactIsAlive(workitem.remoteid)):
            datacount += 1
    dhnio.Dprint(14, "transport_control.SendQueueActiveDataLength returning " + str(datacount))
    return(datacount)

# Count all stuff on the send queue
def SendQueueLength():
    global _SendQueue
    curlen = len(_SendQueue)
    dhnio.Dprint(14, "transport_control.SendQueueLength = " + str(curlen))
    return(curlen)

# Count only active stuff on the send queue
def SendQueueActiveLength():
    global _SendQueue
    count = 0
    for workitem in _SendQueue:
        if ContactIsAlive(workitem.remoteid):
            count += 1
    dhnio.Dprint(14, "transport_control.SendQueueActiveLength = " + str(count))
    return count

def SendQueueAppend(workitem):
    global _SendQueue
    _SendQueue.append(workitem)

# Sometimes we can get an Ack back before transport layer reports status and is done with file.
# So we wait a few seconds to remove file.
# PREPRO Tricky problem is when we are doing a retransmission (sending same again) and get Ack from first time.
def SendQueueRemove(workitem, check_counts = False):
    global _SendQueue
    if check_counts and workitem.counts > 0:
        return
    _SendQueue.remove(workitem)
    if RemoveFileAfterSending():
        #delayeddelete.DeleteAfterTime(workitem.filename, 60)
        tmpfile.throw_out(workitem.filename)

# If we've changed suppliers, we should remove any requests from or data to that supplier
# Only one request exactly like this, so return when found and don't worry about looping through list we modify
def RemoveSupplierRequestFromSendQueue(packetID, supplierIdentity, command):
    for workitem in _SendQueue:
        if (workitem.packetid == packetID) and (workitem.remoteid == supplierIdentity) and (workitem.command == command):
            SendQueueRemove(workitem)
            return

# We only remove after MaxRetries
# Others are removed after sendStatusReport says sent or Ack comes back
def GetFromSendQueue():           # get the next thing that has not been sent yet
    global _SendQueue
    for doAck in [False, True]:            # first pass we do short fast things that don't need an Ack
        for workitem in _SendQueue:
            if workitem.doack == doAck:
                if workitem.status == "presend":
                    workitem.status = "sending"           # leave on queue with sending status
                    workitem.time = time.time()           # need to update time when sending
                    return workitem
                elapsedtime = time.time() - workitem.time
                if (workitem.status == "sending" or workitem.status == "sent") and elapsedtime > workitem.timeout:
                    if workitem.retries == 0:
                        dhnio.Dprint(10, "transport_control.GetFromSendQueue NETERROR could not send to %s after some retries" % nameurl.GetName(workitem.remoteid))
                        SendQueueRemove(workitem)
                    else:
                        dhnio.Dprint(10, "transport_control.GetFromSendQueue NETERROR doing retry to=%s elapsedtime=%s timeout=%s retry=%s" % (nameurl.GetName(workitem.remoteid), str(elapsedtime), str(workitem.timeout), str(workitem.retries)))
                        workitem.time = time.time()              # need to update time when sending
                        workitem.timeout = 2 * workitem.timeout  # exponential backoff for retries
                        #workitem.retries += 1
                        workitem.retries -= 1
                        return workitem
    return None


# We have a Queue of things to send so we can do bandwidth limit and also retry
# Command on Packet does not matter, just remoteid and packetid
def HandleSendQueueAck(packet):
    global _SendQueue
    itemstoremove=[]
    for workitem in _SendQueue:
        if workitem.packetid == packet.PacketID and workitem.remoteid == packet.OwnerID:
            # dhnio.Dprint(14, "transport_control.HandleSendQueueAck removing item with status " + workitem.status)
            itemstoremove.append(workitem)
    for itemtoremove in itemstoremove:
        SendQueueRemove(itemtoremove)       # Also removes filename


#  If time to, take something off the send queue
def ProcessSendQueue():
    global _TimeNextSend
    global _ProcessSendQueueWorker
    global _SendingDelay

    tm = time.time()
    if tm < _TimeNextSend:
        _ProcessSendQueueWorker = reactor.callLater(_TimeNextSend - tm, ProcessSendQueue)
        return

    ret = DoSend()
    if ret == 1:
        _SendingDelay = settings.MinimumSendingDelay()
    else:
        if _SendingDelay < settings.MaximumSendingDelay():
            _SendingDelay *= 2.0
    
    # attenuation
    _ProcessSendQueueWorker = reactor.callLater(_SendingDelay, ProcessSendQueue)


def DoSend():
    global _SupportedProtocols

    workitem = GetFromSendQueue()
    if workitem is None:
        return 0

    if not os.path.exists(workitem.filename):
        dhnio.Dprint(1, "transport_control.DoSend ERROR should never happen that filename not exists " + workitem.filename)
        # raise Exception("transport_control.ProcessSendQueue with non existant filename=" + workitem.filename)
        return -1

    destinationIdentity = contacts.getContact(workitem.remoteid)                #  convert ID to identity
    if destinationIdentity is None:
        dhnio.Dprint(12, "transport_control.DoSend with workitem we don't have identity for - leaving for now")
        return -1

    workitem_sent = False
    for contactmethod in destinationIdentity.getContacts():
        protocol, host, port, filename2 = nameurl.UrlParse(contactmethod)
        if host.strip() == '':
            continue
        if protocol in _SupportedProtocols or protocol == 'tcp':
            SendWorkItem(workitem, protocol, host, port)
            workitem_sent = True
            # we use the first protocol we support
            if not workitem.wide:
                break

    if not workitem_sent:
        dhnio.Dprint(6, 'transport_control.DoSend WARNING no supported protocols with ' + workitem.remoteid)
        return -1

#    if _TransportHTTPEnable and misc.getLocalIdentity().getContactProto(0) == 'http':
#        transport_http.decrease_receiving_delay(workitem.remoteid)

#    if len(_AckWaitingPacketsList) > 100:
#        _AckWaitingPacketsList.pop(0)

    return 1


def SendWorkItem(workitem, protocol, host, port):
    global _TransportEmailEnable
    global _TransportQ2QEnable
    global _TransportSkypeEnable
    global _TimeNextSend
    global _SendFileFunc

    try:
        bytes = os.path.getsize(workitem.filename)
    except:
        dhnio.DprintException()
        bytes = 0
    bandlimit = settings.BandwidthLimit()
    if bandlimit == 0:
        bandlimit = settings.DefaultBandwidthLimit()
    seconds = bytes / bandlimit
    _TimeNextSend = time.time() + seconds

    # if we are to watch for an Ack then set that up
    if workitem.doack:
        # Retrieve is answered with our own Data packet
        if workitem.command == commands.Retrieve():
            RegisterInterest(HandleSendQueueAck, misc.getLocalID(), workitem.packetid)
        else:
            RegisterInterest(HandleSendQueueAck, workitem.remoteid, workitem.packetid)

    filename = workitem.filename

    #bandwidth.OUT(workitem.remoteid, bytes)

    dhnio.Dprint(10, "transport_control.SendWorkItem [%s:%s]->%s://%s:%s (%s) retries=%d" % (str(workitem.command), str(workitem.packetid), protocol, host, port, nameurl.GetName(workitem.remoteid), workitem.retries))

    workitem.started = time.time()

    if protocol == 'http':
        host = workitem.remoteid
    
    workitem.counts += 1
    
    _SendFileFunc(filename, protocol, host, port, workitem.remoteid, bytes, workitem.command)


def SendFile(filename, protocol, host, port, idurl, filesize, command):
    dhnio.Dprint(8, 'transport_control.SendFile %s (%d bytes) to %s://%s:%s, [%s]->[%s]' %
        (os.path.basename(filename), filesize, protocol, host, port, command, nameurl.GetName(idurl)))
    try:
        if protocol == "tcp":
            transport_tcp.send(filename, host, port).addCallbacks(
                lambda x: dhnio.Dprint(18, 'transport_control.SendFile [%s] DONE to %s:%s' % (
                    os.path.basename(filename), host, port)),
                lambda x: dhnio.Dprint(8, 'transport_control.SendFile [%s] FAILED to %s:%s' % (
                    os.path.basename(filename), host, port)),)
            
        elif protocol == "udp":
            if _TransportUDPEnable:
                if command in [commands.Ack(), commands.Identity()]:
                    transport_udp.send(filename, host, port, True)
                else:
                    transport_udp.send(filename, host, port)

        elif protocol == "cspace":
            if _TransportCSpaceEnable:
                transport_cspace.send(host, filename)

        elif protocol == "ssh":
            idname = misc.getLocalID()
            transport_ssh.send(host, port, idname, dhncrypto.MyPublicKey(), dhncrypto.MyPrivateKey(), filename)

        elif protocol == "email":
            if _TransportEmailEnable:
                if settings.getSMTPHost() and settings.getSMTPPort():
                    transport_email.send(filename, host)
                else:
                    transport_email.send_public(filename, host)

        elif protocol == "q2q":
            if _TransportQ2QEnable:
                from_user = settings.getQ2Quserathost()
                transport_q2q.send(host, filename)

        elif protocol == "skype":
            if _TransportSkypeEnable:
                transport_skype.send(host, filename)

        elif protocol == "http":
            if _TransportHTTPEnable:
                transport_http.send(host, filename)

        else:
            dhnio.Dprint(1, "transport_control.SendFile ERROR with protocol we don't handle yet: %s" % protocol )

    except:
        dhnio.Dprint(1, "transport_control.SendFile ERROR with exception:")
        dhnio.DprintException()

_SendFileFunc = SendFile


# Want to shutdown things cleanly so if sending we let it finish
def shutdown():
    global _ShutdownDeferred, _DoingShutdown, _InitDone
    global _InboxPacketCallbacksList
    global _OutboxPacketCallbacksList
    if not _InitDone:
        return succeed(1)
    _InboxPacketCallbacksList = []
    _OutboxPacketCallbacksList = []
    dhnio.Dprint(4, "transport_control.shutdown")
    _DoingShutdown = True
    if SendQueueActiveLength() > 0:
        dhnio.Dprint(6, "transport_control.shutdown making deferred and calling shutdown2")
        _ShutdownDeferred = Deferred()
        reactor.callLater(0, shutdown2)
        return _ShutdownDeferred
    else:
        return shutdown3()


# Here we loop waiting for sends to finish
def shutdown2():
    global _ShutdownCount
    dhnio.Dprint(4,"transport_control.shutdown2 count=" + str(_ShutdownCount))
    _ShutdownCount += 1
    if _ShutdownCount < 10 and SendQueueActiveLength() > 0:
        reactor.callLater(0.1, shutdown2)
    else:
        shutdown3()


# Here we call all the transports to tell them to shutdown and make a deferred from all their deferreds
def shutdown3():
    dhnio.Dprint(4, "transport_control.shutdown3")
    global _ProtocolsListeners
    global _ProtocolsOptions
    global _SupportedProtocols
    global _ShutdownDeferred
    global _TransportHTTPEnable
    global _InitDone
    shutlist=[]
    dhnio.Dprint(6, "transport_control.shutdown3  want to stop %d protocols " % len(_ProtocolsListeners))
    for proto, eachlistener in _ProtocolsListeners.items():
        d = StopProtocol(proto)
        shutlist.append(d)
    _ProtocolsListeners.clear()
    _ProtocolsOptions.clear()
    _SupportedProtocols.clear()
    if _TransportHTTPEnable:
        shutlist.append(transport_http.stop_http_server())
    if len(shutlist) > 0:
        result = DeferredList(shutlist)
        if _ShutdownDeferred is not None:
            result.addCallback(shutdown4)
        return result
    else:
        dhnio.Dprint(6, "transport_control.shutdown3 DeferredList seems BUGGY possible ERROR")
        _InitDone = False
        if _ShutdownDeferred is not None:
            _ShutdownDeferred.callback(1)
            return _ShutdownDeferred
        return succeed(1)


def shutdown4(result):
    global _ShutdownDeferred
    global _InitDone
    dhnio.Dprint(4, "transport_control.shutdown4")
    _InitDone = False
    if _ShutdownDeferred:
        _ShutdownDeferred.callback(result)


#-------------------------------------------------------------------------------


def main():
    dhnio.SetDebug(18)
    init()
    reactor.run()


if __name__ == '__main__':
    main()










