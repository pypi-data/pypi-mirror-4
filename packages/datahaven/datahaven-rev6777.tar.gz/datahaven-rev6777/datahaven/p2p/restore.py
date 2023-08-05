#!/usr/bin/python
#restore.py
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2012
#    All rights reserved.
#
#
#  At least for now we will work one block at a time, though packets in parallel.
#  We ask transport_control for all the data packets for a block then see if we
#  get them all or need to ask for some parity packets.  We do this till we have
#  gotten a block with the "LastBlock" flag set.  If we have tried several times
#  and not gotten data packets from a supplier we can flag him as suspect-bad
#  and start requesting a parity packet to cover him right away.
#
#  When we are missing a data packet we pick a parity packet where we have all the
#  other data packets for that parity so we can recover the missing data packet.
#  This network cost for this is just as low as if we read the data packet.
#  But most of the time we won't bother reading the parities.  Just uses up bandwidth.
#
#    We don't want to fire someone till
#    after we have finished a restore in case we have other problems and they might come
#    back to life and save us.  However, we might keep packets for a node we plan to fire.
#    This would make replacing them very easy.
#
#  At the "tar" level a user will have choice of full restore (to new empty system probably)
#  or to restore to another location on disk, or to just recover certain files.  However,
#  in this module we have to read block by block all of the blocks.
#
#
# How do we restore if we lost everything?
#     Our ( public/private-key and eccmap) could be:
#                  1)  at DHN  (encrypted with pass phrase)
#                  2)  on USB in safe or deposit box   (encrypted with passphrase or clear text)
#                  3)  with friends or scrubbers (encrypted with passphrase)
# The other thing we need is the backupIDs which we can get from our suppliers with the ListFiles command.
# The ID is something like   F200801161206  or I200801170401 indicating full or incremental.

import os
import sys
import tempfile
import time

try:
    from twisted.internet import reactor
except:
    sys.exit('Error initializing twisted.internet.reactor in restore.py')


from twisted.internet.defer import Deferred


import lib.misc as misc
import lib.dhnio as dhnio
##import lib.dhnpacket as dhnpacket
import lib.eccmap as eccmap
import lib.dhncrypto as dhncrypto
#import lib.transport_control as transport_control
import lib.settings as settings
import lib.packetid as packetid
import lib.contacts as contacts
import lib.tmpfile as tmpfile


import raidread
import dhnblock
#import guistatus
import io_throttle
import events


#------------------------------------------------------------------------------ 


class restore:
    def __init__(self, BackupID, OutputFile): # OutputFileName 
        dhnio.Dprint(6, "restore.restore init for backup " + BackupID + ", ecc " + eccmap.CurrentName())
        self.CreatorID = misc.getLocalID()
        self.BackupID = BackupID
        #self.File = open(OutputFileName, "wb")
        self.File = OutputFile
        # is current active block - so when add 1 we get to first, which is 0
        self.BlockNumber = -1              
        self.OnHandData = []
        self.OnHandParity = []
        self.AbortState = False
        self.Done = False
        self.EccMap = eccmap.Current()
        self.LastAction = time.time()
        # Check how things are going every second
        self.PollTime = 1
        # For anyone who wants to know when we finish
        self.MyDeferred = Deferred()       
        self.packetInCallback = None
        
        events.info('restore', 'start restoring backup %s' % self.BackupID)
        
        reactor.callLater(.01, self.StartNewBlock)
        reactor.callLater(self.PollTime, self.MonitorLoop) # Get polling loop going


    def SetPacketInCallback(self, cb):
        self.packetInCallback = cb


    def PacketCameIn(self, NewPacket):
        if self.AbortState:
            return
        
        self.LastAction = time.time()
        #dhnio.Dprint(12, "restore.PacketCameIn seeing BlockNumber %s while on %s " % (NewPacket.BlockNumber(), self.BlockNumber))

        if NewPacket.BlockNumber() != str(self.BlockNumber):
            dhnio.Dprint(6, "restore.PacketCameIn WARNING ignoring old packet "+ str(NewPacket.BlockNumber()) + "-"+ str(NewPacket.SupplierNumber())+ " while on "+ str(self.BlockNumber))
            return

        SupplierNumber = packetid.SupplierNumber(NewPacket.PacketID)

        if NewPacket.DataOrParity() == misc.Data():
            self.OnHandData[SupplierNumber] = True
            fname = self.BackupID + "-" + str(self.BlockNumber) + "-" + str(SupplierNumber) + "-Data"

        elif NewPacket.DataOrParity() == misc.Parity():
            self.OnHandParity[SupplierNumber] = True
            fname = self.BackupID + "-" + str(self.BlockNumber) + "-" + str(SupplierNumber) + "-Parity"

        else:
            dhnio.Dprint(2, "restore.PacketCameIn ERROR %s is not Data or Parity" % NewPacket.BlockNumber())
            self.FailStop()
            return
        
        if self.packetInCallback is not None:
            self.packetInCallback(self.BackupID, NewPacket)

        # filename = os.path.join(tmpfile.subdir('data-par'), fname)
        filename = os.path.join(settings.getLocalBackupsDir(), fname)

        # either way the payload of packet is saved
        dhnio.WriteFile(filename, NewPacket.Payload)                
        dhnio.Dprint(12, "restore.PacketCameIn saved as " + filename)

        if self.EccMap.Fixable(self.OnHandData, self.OnHandParity):
            io_throttle.DeleteBackupRequests(self.BackupID + "-" + str(self.BlockNumber))
            self.PacketsToBlock()


    def PacketsToBlock(self):
        if self.AbortState:
            return
        
        self.LastAction = time.time()
        dhnio.Dprint(6, "restore.PacketsToBlock - starting - block " + str(self.BlockNumber))
        
        io_throttle.DeleteBackupRequests(self.BackupID + "-" + str(self.BlockNumber))
        
        #filename = os.path.join(tmpfile.subdir('data-par'), "newblock-" + self.BackupID)
        filename = os.path.join(settings.getLocalBackupsDir(), "newblock-" + self.BackupID)

        raidread.raidread(filename, eccmap.CurrentName(), self.BackupID, self.BlockNumber)
        blockbits = dhnio.ReadBinaryFile(filename)
        splitindex = blockbits.index(":")
        lengthstring = blockbits[0:splitindex]
        try:
            #dhnio.Dprint(10, "restore.PacketsToBlock - BlockNumber=%s  splitindex=%s lengthstring=%s " % (self.BlockNumber, splitindex, lengthstring))
            datalength = int(lengthstring)                                  # real length before raidmake/ECC
            blockdata = blockbits[splitindex+1:splitindex+1+datalength]     # remove padding from raidmake/ECC
            #dhnio.Dprint(10, "restore.PacketsToBlock - got blockdata len is %s" % len(blockdata))
            newblock = dhnblock.Unserialize(blockdata)                        # convert to object
            #dhnio.Dprint(10, "restore.PacketsToBlock - Unserialize worked ")
        except:
            self.FailStop()
            return
        
        if newblock is None:
            self.FailStop()
            return

        if not newblock.Valid():
            self.FailStop()
            return
        
        dhnio.Dprint(6, "restore.PacketsToBlock " + str(newblock))

        SessionKey = dhncrypto.DecryptLocalPK(newblock.EncryptedSessionKey)
        paddeddata = dhncrypto.DecryptWithSessionKey(SessionKey, newblock.EncryptedData)
        newlen = int(newblock.Length)
        data = paddeddata[:newlen]
        try:
            self.File.write(data)
            # Add to the file where all the data is going
        except:
            pass

        if newblock.LastBlock == str(True):
            dhnio.Dprint(2, "restore.PacketsToBlock has finished EOF block.") 
            reactor.callLater(.01,self.RestoreComplete)
        else:
            reactor.callLater(.01,self.StartNewBlock)


    # PREPRO - right now we fetch all the parities.
    # Could save bandwidth by only fetching needed ones.
    def StartNewBlock(self):
        if self.AbortState:
            return
        self.LastAction = time.time()
        self.BlockNumber += 1                               # current one we are putting together
        dhnio.Dprint(12, "restore.StartNewBlock " + str(self.BlockNumber))
        self.OnHandData=[False]*self.EccMap.datasegments
        self.OnHandParity=[False]*self.EccMap.paritysegments
        self.DoNeededRequests()


    def DoNeededRequests(self):
        packetsToRequest = self.GetPacketNeeds()

        if self.EccMap.Fixable(self.OnHandData, self.OnHandParity):
            dhnio.Dprint(2, "restore.StartNewBlock We have enough data to make block " + str(self.BlockNumber))
            reactor.callLater(.01, self.PacketsToBlock)
            
        else:
            for packetId in packetsToRequest:
                SupplierNumber = packetId[0:packetId.rfind("-")]
                SupplierNumber = SupplierNumber[SupplierNumber.rfind("-")+1]
                io_throttle.QueueRequestFile(
                    self.PacketCameIn, 
                    self.CreatorID, 
                    packetId, 
                    self.CreatorID, 
                    contacts.getSupplierID(SupplierNumber))


    def GetPacketNeeds(self):
        packetsToRequest = []

        for SupplierNumber in range(self.EccMap.datasegments):
            PacketID = packetid.MakePacketID(self.BackupID, self.BlockNumber, misc.Data(), SupplierNumber)
            # if os.path.exists(os.path.join(tmpfile.subdir('data-par'), PacketID)):
            if os.path.exists(os.path.join(settings.getLocalBackupsDir(), PacketID)):
                self.OnHandData[SupplierNumber] = True
            else:
                packetsToRequest.append(PacketID)
                
        for SupplierNumber in range(self.EccMap.paritysegments):
            PacketID = packetid.MakePacketID(self.BackupID, self.BlockNumber, misc.Parity(), SupplierNumber)
            # if os.path.exists(os.path.join(tmpfile.subdir('data-par'), PacketID)):
            if os.path.exists(os.path.join(settings.getLocalBackupsDir(), PacketID)):
                self.OnHandParity[SupplierNumber] = True
            else:
                packetsToRequest.append(PacketID)
                
        return packetsToRequest


#    def CountOnHandPackets(self, onHandList):
#        result=0
#        for eachitem in onHandList:
#            if (eachitem==True):
#                result += 1
#        return(result)


#    #  Could do something more here PREPRO
#    def CheckOnBlock(self):
#        dhnio.Dprint(12, "restore.CheckOnBlock OnHandData=" + str(self.CountOnHandPackets(self.OnHandData)) + "   Parity="+ str(self.CountOnHandPackets(self.OnHandParity)) + " Fixable=" + str(self.EccMap.Fixable(self.OnHandData, self.OnHandParity)))


    def MonitorLoop(self):
        dhnio.Dprint(12, "restore.MonitorLoop")

        if not self.Done:
            if self.AbortState:
                self.CloseWithAbort()
                return
            
            # if we've not done anything in last 60 seconds 
            # (no requests, no incoming, no block rebuilds), 
            # make sure we're on track)
            if time.time() - self.LastAction > 60:
                reactor.callLater(.01, self.DoNeededRequests)
                
            reactor.callLater(self.PollTime, self.MonitorLoop)
            
        else:
            dhnio.Dprint(12, "restore.ReadLoop AtEOF")             # no more CallMeLater


    def FailStop(self):  # when we have an error in the restore, stop
        dhnio.Dprint(1, "restore.FailStop ERROR - new block does not look good")
        self.File.close()
        self.Done = True
        io_throttle.DeleteBackupRequests(self.BackupID + "-")
        self.MyDeferred.errback(self.BackupID+" Bad Block!!!")
        events.notify('restore', 'backup %s: failed to restore block number %d' % (self.BackupID, self.BlockNumber))


    def RestoreComplete(self):
        dhnio.Dprint(2, "restore.RestoreComplete - restore has finished. All is well that ends well.")
        self.File.close()
        self.Done = True
        io_throttle.DeleteBackupRequests(self.BackupID + "-")
        self.MyDeferred.callback(self.BackupID+' done')
        events.info('restore', 'backup %s restored successfully')


    def CloseWithAbort(self):
        dhnio.Dprint(8, "restore.CloseWithAbort")
        self.File.close()
        self.Done = True
        io_throttle.DeleteBackupRequests(self.BackupID + "-")
        self.MyDeferred.callback(self.BackupID+' aborted')   # succeed
        events.info('restore', 'restoring of backup %s were aborted')


    def Abort(self): # for when user clicks the Abort restore button on the gui
        dhnio.Dprint(8, "restore.Abort")
        self.AbortState = True

