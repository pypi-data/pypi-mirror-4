#!/usr/bin/python
#customerservice.py
#
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2012
#    Use of this software constitutes acceptance of the Terms of Use
#      http://datahaven.net/terms_of_use.html
#    All rights reserved.
#
#
# This serves requests from customers.
#     Data          - save packet to a file      (a commands.Data() packet)
#     Retrieve      - read packet from a file    (a commands.Data() packet)
#     ListFiles     - list files we have for customer
#     Delete        - delete a file
#     Identity      - contact or id server sending us a current identity
#
# For listed customers we will save and retrieve data up to their specified limits.
#   DHN tells us who our customers are and limits, we get their identities.
#   If a customer does not contact us for more than 30 hours (or something) then we can process
#       requests from that customers scrubbers
#
# Security:
#
#     Transport_control has checked that it is signed by a contact, 
#       but we need to check that this is a customer.
#
#     Since we have control over suppliers, and may not change them much,
#       it feels like customers are more of a risk.
#
#     Code treats suppliers and customers differently.  Fun that stores
#       have customers come in the front door and suppliers in the back door.
#     But I don't see anything really worth doing.
#         On Unix machines we could run customers in a chrooted environment.
#         There would be a main datahaven code and any time it got a change
#         in the list of customers, it could restart the customer code.
#         The customer code could be kept very small this way.
#         Again, I doubt it.  We only have XML and binary.
#     Real risk is probably the code for SSH, Email, Vetex, etc.
#         Once it is a dhnpacket object, we are probably ok.
#
#  We will store in a file and be able to read it back when requested.
#  Request comes as a dhnpacket and we just
#
#  Resource limits - localtester checks that someone is not trying to use more than they are supposed to
#                  - we could also do it here .   PREPRO
#

import os
import sys
import time


try:
    from twisted.internet import reactor
except:
    sys.exit('Error initializing twisted.internet.reactor in customerservice.py')

from twisted.internet.defer import Deferred


import lib.dhnpacket as dhnpacket
import lib.contacts as contacts
import lib.commands as commands
import lib.misc as misc
import lib.dhnio as dhnio
import lib.eccmap as eccmap
import lib.settings as settings
import lib.transport_control as transport_control
import lib.identity as identity
import lib.identitycache as identitycache
import lib.packetid as packetid
import lib.nameurl as nameurl


import message
import backups
import localtester
#import summary


_TrafficInFunc = None
_TrafficOutFunc = None

#_InboxStatusIOThrottleFunc = None
#_OutboxStatusIOThrottleFunc = None

#------------------------------------------------------------------------------

def SetTrafficInFunc(f):
    global _TrafficInFunc
    _TrafficInFunc = f

def SetTrafficOutFunc(f):
    global _TrafficOutFunc
    _TrafficOutFunc = f

#def SetInboxStatusIOThrottleFunc(f):
#    global _InboxStatusIOThrottleFunc
#    _InboxStatusIOThrottleFunc = f
#
#def SetOutboxStatusIOThrottleFunc(f):
#    global _OutboxStatusIOThrottleFunc
#    _OutboxStatusIOThrottleFunc = f

#------------------------------------------------------------------------------

def init():
    dhnio.Dprint(4, 'customerservice.init')
    transport_control.AddInboxCallback(inbox)
    transport_control.AddInboxPacketStatusFunc(inbox_status)
    transport_control.AddOutboxPacketStatusFunc(outbox_status)
    transport_control.SetMessageFunc(message2gui)

#------------------------------------------------------------------------------

def inbox(newpacket, proto='', host=''):
    if newpacket.Command == commands.Identity():
        Identity(newpacket)            # contact sending us current identity we might not have
        return True

    if newpacket.Valid():              # check that signed by a contact of ours
        if newpacket.CreatorID == misc.getLocalID() or newpacket.RemoteID == misc.getLocalID():
            handled = inboxPacket(newpacket, proto, host)
            if handled:
                dhnio.Dprint(12, "customerservice.inbox [%s] from %s (%s://%s) handled" % (newpacket.Command, nameurl.GetName(newpacket.CreatorID), proto, host))
            return handled

        else:
            dhnio.Dprint(1, "customerservice.inbox  ERROR packet is NOT for us")
            dhnio.Dprint(1, "customerservice.inbox  getLocalID=" + misc.getLocalID() )
            dhnio.Dprint(1, "customerservice.inbox  CreatorID=" + newpacket.CreatorID )
            dhnio.Dprint(1, "customerservice.inbox  RemoteID=" + newpacket.RemoteID )
            dhnio.Dprint(1, "customerservice.inbox  PacketID=" + newpacket.PacketID )
            return False

    else:
        dhnio.Dprint(1, 'customerservice.inbox ERROR new packet is not Valid')
        return False


# Packet has been checked and is Valid()
def inboxPacket(newpacket, proto, host):
    commandhandled = False
    if newpacket.Command == commands.Fail():
        dhnio.Dprint(6, "customerservice.inboxPacket has a commands.Fail ")
        return

    if newpacket.Command == commands.Retrieve():
        # retrieve some packet customer stored with us
        Retrieve(newpacket)
        commandhandled = True

    elif newpacket.Command==commands.Ack():
        # With Ack we just need FindInterestedParty() below
        commandhandled = True

    elif newpacket.Command == commands.Data():
        # new packet to store for customer
        Data(newpacket)
        commandhandled = True

    elif newpacket.Command == commands.ListFiles():
        # customer wants list of their files
        ListFiles(newpacket)
        commandhandled = True

    elif newpacket.Command == commands.Files():
        # supplier sent us list of files
        Files(newpacket)
        commandhandled = True

    elif newpacket.Command == commands.Files():
        commandhandled = True

    elif newpacket.Command == commands.DeleteFile():
        # will Delete a customer file for them
        DeleteFile(newpacket)
        commandhandled = True

    elif newpacket.Command == commands.DeleteBackup():
        # will Delete all files starting in a backup
        DeleteBackup(newpacket)
        commandhandled = True

    elif newpacket.Command == commands.RequestIdentity():
        # contact asking for our current identity
        RequestIdentity(newpacket)
        commandhandled = True

    elif newpacket.Command == commands.Message():
        # someone sent us a message
        message.Message(newpacket)
        commandhandled = True

    elif newpacket.Command == commands.Correspondent():
        # someone want to be our correspondent
        Correspondent(newpacket)

    return commandhandled


def outbox(outpacket):
    dhnio.Dprint(8, "customerservice.outbox [%s] to %s" % (outpacket.Command, nameurl.GetName(outpacket.RemoteID)))
    return True


def inbox_status(newpacket, status, proto, host, error, message):
    global _InboxStatusIOThrottleFunc
    global _TrafficInFunc

    if _TrafficInFunc is not None:
        _TrafficInFunc(newpacket, status, proto, host, error, message)


def outbox_status(workitem, proto, host, status, error, message):
#    global _OutboxStatusIOThrottleFunc
    global _TrafficOutFunc

#    if _OutboxStatusIOThrottleFunc is not None:
#        _OutboxStatusIOThrottleFunc(workitem, proto, host, status, error, message)

    if _TrafficOutFunc is not None:
        _TrafficOutFunc(workitem, proto, host, status, error, message)

#    if host is None:
#        status_str = message
#        error_str = getErrorString(error)
#        if error_str:
#            status_str += ': ' + error_str
#        message2gui(proto, status_str)
#        return

#------------------------------------------------------------------------------ 

# Must be a customer, and then we make full path filename for where this packet is stored locally
# SECURITY
def makeFilename(custid, custpacketid):
    if not contacts.IsCustomer(custid):  # SECURITY
        dhnio.Dprint(4, "customerservice.makeFilename WARNING %s not a customer: %s" % (custid, str(contacts.getCustomerNames())))
        return ''
    if not packetid.Valid(custpacketid) and custpacketid != settings.BackupInfoFileName(): # SECURITY
        dhnio.Dprint(1, "customerservice.makeFilename WARNING failed packetid format: " + custpacketid )
        return ''
    contactnum = nameurl.UrlFilename(custid)
    custdir = settings.getCustomersFilesDir()
    if not os.path.exists(custdir):
        dhnio._dir_make(custdir)
    ownerdir = os.path.join(custdir, contactnum)
    if not os.path.exists(ownerdir):
        dhnio._dir_make(ownerdir)
    filename = os.path.join(ownerdir, custpacketid)
    return filename

#------------------------------------------------------------------------------

# Save the customer file on our local HDD
def Data(request):
    dhnio.Dprint(6, "customerservice.Data owner:[%s] creator:[%s] remote:[%s] packetID:%s" % (
        nameurl.GetName(request.OwnerID), nameurl.GetName(request.CreatorID), nameurl.GetName(request.RemoteID), request.PacketID,))
    filename = makeFilename(request.OwnerID, request.PacketID)
    if filename == "":
        if request.OwnerID == misc.getLocalID():
            dhnio.Dprint(6, "customerservice.Save has data packet we restore requested " + request.PacketID)
        else:
            dhnio.Dprint(1,"customerservice.Save WARNING had bogus customer " + request.OwnerID)
        return
    data = request.Serialize()
    if not dhnio.WriteFile(filename, data):
        dhnio.Dprint(1, "customerservice.Data ERROR can not write to " + str(filename))
        return
    transport_control.SendAck(request, str(len(request.Payload)))
    reactor.callLater(3, localtester.TestSpaceTime)
    del data


# Delete one file
def DeleteFile(request):
    filename = makeFilename(request.OwnerID, request.PacketID)
    if filename == "":
        dhnio.Dprint(1,"customerservice.DeleteFile WARNING had bogus customer " + request.OwnerID + " or PacketID " + request.PacketID)
        return

    dhnio.Dprint(6, "customerservice.Delete with " + filename)
    if (os.path.exists(filename)):
        os.remove(filename)
    transport_control.SendAck(request)


# Delete all files starting with
def DeleteBackup(request):
    filename = makeFilename(request.OwnerID, request.PacketID)
    if filename == "":
        dhnio.Dprint(1,"customerservice.DeleteBackup WARNING had bogus customer " + request.OwnerID + " or PacketID " + request.PacketID)
        return
    dhnio.Dprint(6,"customerservice.DeleteBackup with " + filename)
    dirpath = os.path.dirname(filename)
    basename = os.path.basename(filename)
    dirList = os.listdir(dirpath)
    for fname in dirList:
        if fname.startswith(basename):
            filetoremove = os.path.join(dirpath, fname)
            dhnio.Dprint(12, "customerservice.DeleteBackup about to delete %s " % filetoremove)
            try:
                os.remove(filetoremove)
            except:
                dhnio.DprintException()
    transport_control.SendAck(request)


def SendDeleteBackup(SupplierID, BackupID):
    dhnio.Dprint(6, "customerservice.SendDeleteBackup SupplierID=%s  BackupID=%s " % (SupplierID, BackupID))
    MyID = misc.getLocalID()
    PacketID = BackupID
    RemoteID = SupplierID
    result = dhnpacket.dhnpacket(commands.DeleteBackup(),  MyID, MyID, PacketID, "", RemoteID)
    transport_control.outboxAck(result)


# Contact or identity server is sending us a new copy of an identity for a contact of ours
def Identity(newpacket):
    newxml = newpacket.Payload
    newidentity = identity.identity(xmlsrc=newxml)

    # SECURITY - check that identity is signed correctly
    if not newidentity.Valid():
        dhnio.Dprint(1,"customerservice.Identity ERROR has non-Valid identity")
        return

    idurl = newidentity.getIDURL()

    if contacts.isKnown(idurl):
        # This checks that old public key matches new
        identitycache.UpdateAfterChecking(idurl, newxml)

    else:
        # TODO
        # may be we need to make some temporary storage
        # for identities who we did not know yet
        # just to be able to receive packets from them
        identitycache.UpdateAfterChecking(idurl, newxml)

    # Now that we have ID we can check packet
    if not newpacket.Valid():
        # If not valid do nothing
        return

    # Save remote Identity to identity cache, so this user can send a packets to us
#    if IdIsNew:
#        identitycache.UpdateAfterChecking(idurl, newxml)

    if newpacket.OwnerID == idurl:
        transport_control.SendAck(newpacket)


TossAfter=0


def InitTossAfter():
    cmap = eccmap.Current()
    TossAfter=cmap.DataNeeded()


#  Customer is asking us for data he previously stored with us.
#  We send with outboxNoAck because he will ask again if he does not get it
def Retrieve(request):
    filename = makeFilename(request.OwnerID, request.PacketID)
    if filename == "":
        dhnio.Dprint(1,"customerservice.Retrieve WARNING had bogus customer " + request.OwnerID)
        return

##    print "customerservice.Retrieve with filename ", filename
#    if (dhnio.Debug(25)):
#        global TossAfter
#        if (TossAfter==0):
#            InitTossAfter()
#        if (request.SupplierNumber() > TossAfter):    # Ok to mess with some of the
#            if (100*random.random() <= 70):           # 70% chance of packet on safe subset of nodes
#                print "DEBUG customerservice.Retrieve is dropping a packet ", misc.DebugLevel
#                return

    if os.path.exists(filename):
        data = dhnio.ReadBinaryFile(filename)
        packet = dhnpacket.Unserialize(data)
        del data 
        if packet.Valid():
            dhnio.Dprint(6, "customerservice.Retrieve sending back to " + nameurl.GetName(packet.CreatorID))
            transport_control.outboxNoAck(packet)
        else:
            dhnio.Dprint(1, "customerservice.Retrieve ERROR found data on disk not Valid packet " + filename)
    else:
        dhnio.Dprint(1, "customerservice.Retrieve ERROR did not find requested packet " + filename)
    return                                           # PREPRO - probably should be a fail dhnpacket or something else


# We will want to use this to see what needs to be resent, and expect normal case is very few missing.
# This is to build the Files we are holding for a customer
def ListFiles(request):
    custnum = nameurl.UrlFilename(request.OwnerID)
    dhnio.Dprint(6, "customerservice.ListFiles from [%s]" % nameurl.GetName(request.OwnerID))
    MyID = misc.getLocalID()
    RemoteID = request.OwnerID
    PacketID = request.PacketID
    Payload = request.Payload
    custdir = settings.getCustomersFilesDir()
    ownerdir = os.path.join(custdir, custnum)
    #dhnio.Dprint(12, "customerservice.ListFiles have ownerdir= " + ownerdir)
    if not os.path.isdir(ownerdir):
        dhnio.Dprint(8, "customerservice.ListFiles did not find customer dir " + ownerdir)
        result = dhnpacket.dhnpacket(commands.Files(),  MyID, MyID, PacketID, '', RemoteID)
        transport_control.outboxNoAck(result)
        return
    dirlist = os.listdir(ownerdir)
    dirtxt = "".join(map(misc.AddNL, dirlist))
    listresult = dirtxt                             #  default is plain text
    if Payload == "Text":
        listresult = dirtxt
    elif Payload == "Compressed":
        listresult = zlib.compress(dirtxt)
    elif Payload == "Summary":
        listresult = ListSummary(dirlist)
        dhnio.Dprint(12, "customerservice.ListFiles returning " + listresult)
    result = dhnpacket.dhnpacket(commands.Files(),  MyID, MyID, PacketID, listresult, RemoteID)
    transport_control.outboxNoAck(result)


# on the status form when clicking on a customer, find out what files we're holding for that customer
def ListCustomerFiles(customerNumber):
    idurl = contacts.getCustomerID(customerNumber)
    filename = nameurl.UrlFilename(idurl)
    customerDir = os.path.join(settings.getCustomersFilesDir(), filename)
    if os.path.exists(customerDir) and os.path.isdir(customerDir):
        backupFilesList = os.listdir(customerDir)
        if len(backupFilesList) > 0:
            return ListSummary(backupFilesList)
    return "No files stored for this customer"


def RequestListFilesAll():
    r = []
    for supi in range(contacts.numSuppliers()):
        r.append(RequestListFiles(supi))
    return r


def RequestListFiles(supplierNumORidurl):
    if isinstance(supplierNumORidurl, str):
        RemoteID = supplierNumORidurl
    else:
        RemoteID = contacts.getSupplierID(supplierNumORidurl)
    if not RemoteID:
        dhnio.Dprint(6, "customerservice.RequestListFiles WARNING RemoteID is empty supplierNumORidurl=%s" % str(supplierNumORidurl))
        return
    dhnio.Dprint(6, "customerservice.RequestListFiles [%s]" % nameurl.GetName(RemoteID))
    MyID = misc.getLocalID()
    PacketID = packetid.UniqueID()
    Payload = settings.ListFilesFormat()
    result = dhnpacket.dhnpacket(commands.ListFiles(), MyID, MyID, PacketID, Payload, RemoteID)
    transport_control.outboxNoAck(result)
    return PacketID


# Take directory listing and make summary of format:
#         BackupID-1-Data 1-1873 missing for 773,883,
#         BackupID-1-Parity 1-1873 missing for 777,982,
def ListSummary(dirlist):
    BackupMax={}
    BackupAll={}
    result=""

    for filename in dirlist:
        if not packetid.Valid(filename):       # if not type we can summarize
            result += filename + "\n"            #    then just include filename
        else:
            BackupID, BlockNum, SupNum, DataOrParity = packetid.BidBnSnDp(filename)
            LocalID = BackupID + "-" + SupNum + "-" + DataOrParity
            blocknum = int(BlockNum)
            BackupAll[(LocalID,blocknum)]=True
            if LocalID in BackupMax:
                if BackupMax[LocalID] < blocknum:
                    BackupMax[LocalID] = blocknum
            else:
                BackupMax[LocalID] = blocknum

    for BackupName in sorted(BackupMax.keys()):
        missing = []
        thismax = BackupMax[BackupName]
        for blocknum in range(0, thismax):
            if not (BackupName, blocknum) in BackupAll:
                missing.append(str(blocknum))

        result += BackupName + " from 0-" + str(thismax)
        if len(missing) > 0:
            result += ' missing '
            result += ','.join(missing)
#            for m in missing:
#                result += str(m) + ","
        result += "\n"

    return result


# A directory list came in from some supplier
def Files(packet):
    dhnio.Dprint(6, "customerservice.Files from [%s]" % nameurl.GetName(packet.OwnerID))
    statustext = ''
    if settings.ListFilesFormat() == "Text":
        statustext = packet.Payload
    elif settings.ListFilesFormat() == "Compressed":
        statustext = zlib.decompress(packet.Payload)
    elif settings.ListFilesFormat() == "Summary":
        statustext = packet.Payload

    # comment lines start with blank space " "
    if statustext.strip() != '':
        statustext = "" + packet.OwnerID + "\n" + statustext
    else:
        statustext = "" + packet.OwnerID + "\n"

    num = contacts.numberForSupplier(packet.OwnerID)
    if num != -1:
        backups.IncomingListFiles(num, packet, statustext)
#        if backup_monitor.IncomingListFiles is not None:
#            backup_monitor.IncomingListFiles(num, packet, statustext)


# we need to send a DeleteBackup command to all suppliers
def RequestDeleteBackup(BackupID):
    dhnio.Dprint(4, "customerservice.RequestDeleteBackup with BackupID=" + str(BackupID))
    #backups.DeleteBackup(BackupID)
    #backup_monitor.DeleteBackup(BackupID)
    for supplier in contacts.getSupplierIDs():
        if supplier.strip() != '':
            SendDeleteBackup(supplier, BackupID)


def RequestDeleteListBackups(backupIDs):
    dhnio.Dprint(4, "customerservice.RequestDeleteListBackups wish to delete %d backups" % len(backupIDs))
    if len(backupIDs) > 10:
        # we can remove other backups later
        backupIDs = backupIDs[:10]
    for backupID in backupIDs:
        if backupID != '':
            RequestDeleteBackup(backupID)


def CheckWholeBackup(BackupID):
    dhnio.Dprint(6, "customerservice.CheckWholeBackup with BackupID=" + BackupID)


# Someone is requesting a copy of our current identity.
# Transport_control has verified that they are a contact.
# Can also be used as a sort of "ping" test to make sure we are alive.
def RequestIdentity(request):
    dhnio.Dprint(6, "customerservice.RequestIdentity starting")
##    contactnum = str(contacts.numberForCustomer(request.OwnerID))
##    dhnio.Dprint(6, "customerservice.RequestIdentity have contactnum= " + contactnum)
    MyID = misc.getLocalID()
    RemoteID = request.OwnerID
    PacketID = request.PacketID
    identitystr = misc.getLocalIdentity().serialize()
    dhnio.Dprint(12, "customerservice.RequestIdentity returning ")
    result = dhnpacket.dhnpacket(commands.Identity(), MyID, MyID, PacketID, identitystr, RemoteID)
    transport_control.outboxNoAck(result)


def Correspondent(request):
    dhnio.Dprint(6, "customerservice.Correspondent")
    MyID = misc.getLocalID()
    RemoteID = request.OwnerID
    PacketID = request.PacketID
    Msg = misc.decode64(request.Payload)
    # TODO !!!

#-------------------------------------------------------------------------------

def message2gui(proto, text):
    pass
#    statusline.setp(proto, text)


def getErrorString(error):
    try:
        return error.getErrorMessage()
    except:
        if error is None:
            return ''
        return str(error)


def getHostString(host):
    try:
        return str(host.host)+':'+str(host.port)
    except:
        if host is None:
            return ''
        return str(host)



