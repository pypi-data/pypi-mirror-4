#!/usr/bin/python
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2012
#    All rights reserved.
#
# packetid  - we have a standard way of making the PacketID strings for many packets.

# Note we return strings and not integers

import time

lastunique=0
sep="-"

def UniqueID():
    global lastunique
    lastunique += 1
    # we wrap around every billion, old packets should be gone by then
    if lastunique > 1000000000:     
        lastunique = 0
    inttime = int(time.time() * 100.0)
    if lastunique < inttime:
        lastunique = inttime
    # strings for packet fields
    return str(lastunique) 

def MakePacketID(BackupID, BlockNumber, DataOrParity, SupplierNumber):
    global sep
    PacketID = BackupID + sep + str(BlockNumber) + sep + str(SupplierNumber) + sep + DataOrParity
    if not Valid(PacketID):
        raise Exception("packetid.MakePacketID has invalid arguments " + PacketID)
    return PacketID

def Valid(PacketID):
    global sep
    # all parts alpha numeric is good
    if PacketID.isalnum():
        return True
    # 4 parts to valid PacketID
    pidlist = PacketID.split(sep)
    if len(pidlist) != 4:            
        return False
    # all parts must be alpha numeric
    for part in pidlist:
        if not part.isalnum():       
            return False
    return True

def BidBnSnDp(PacketID):
    global sep
    pidlist = PacketID.split(sep)
    return pidlist

def BackupID(PacketID):
    global sep
    pidlist = PacketID.split(sep)
    if (len(pidlist)>=1):
        return(pidlist[0])
    return ""

def BlockNumber(PacketID):
    global sep
    pidlist = PacketID.split(sep)
    if (len(pidlist)>=2):
        return(pidlist[1])
    return ""

def SupplierNumber(PacketID):
    global sep
    pidlist = PacketID.split(sep)
    if (len(pidlist)>=3):
        return(int(pidlist[2]))
    return ""

def DataOrParity(PacketID):
    global sep
    pidlist = PacketID.split(sep)
    if (len(pidlist)>=4):
        return(pidlist[3])
    return ""
