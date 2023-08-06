#!/usr/bin/python
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2013
#    Use of this software constitutes acceptance of the Terms of Use
#      http://datahaven.net/terms_of_use.html
#    All rights reserved.
#
# packetid  - we have a standard way of making the PacketID strings for many packets.

# Note we return strings and not integers

import time

lastunique=0
sep = "-"

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

def MakePacketID(backupID, blockNumber, supplierNumber, dataORparity):
    global sep
    PacketID = backupID + sep + str(blockNumber) + sep + str(supplierNumber) + sep + dataORparity
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

def BidBnSnDp(packetID):
    global sep
    try:
        backupID, blockNum, supplierNum, dataORparity = packetID.split(sep)
        blockNum = int(blockNum)
        supplierNum =  int(supplierNum)
    except:
        return None, None, None, None
    return backupID, blockNum, supplierNum, dataORparity

def BackupID(PacketID):
    global sep
    pidlist = PacketID.split(sep)
    if (len(pidlist)>=1):
        return pidlist[0]
    return None

def BlockNumber(PacketID):
    global sep
    pidlist = PacketID.split(sep)
    if len(pidlist) >= 2:
        return int(pidlist[1])
    return None

def SupplierNumber(PacketID):
    global sep
    pidlist = PacketID.split(sep)
    if len(pidlist) >= 3:
        return int(pidlist[2])
    return None

def DataOrParity(PacketID):
    global sep
    pidlist = PacketID.split(sep)
    if len(pidlist) >= 4:
        return pidlist[3]
    return None
