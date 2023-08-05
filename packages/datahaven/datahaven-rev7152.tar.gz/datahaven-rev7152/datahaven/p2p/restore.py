#!/usr/bin/python
#restore.py
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2012
#    Use of this software constitutes acceptance of the Terms of Use
#      http://datahaven.net/terms_of_use.html
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
        
        events.info('restore', '%s start restoring' % self.BackupID)
        
        reactor.callLater(0, self.StartNewBlock)
        reactor.callLater(self.PollTime, self.MonitorLoop) # Get polling loop going


    def SetPacketInCallback(self, cb):
        self.packetInCallback = cb


    def PacketCameIn(self, NewPacket, state):
        if self.AbortState:
            return
        if state == 'received':
            self.LastAction = time.time()
            if NewPacket.BlockNumber() != str(self.BlockNumber):
                dhnio.Dprint(6, "restore.PacketCameIn WARNING ignoring old packet "+ str(NewPacket.BlockNumber()) + "-"+ str(NewPacket.SupplierNumber())+ " while on "+ str(self.BlockNumber))
                return
            SupplierNumber = packetid.SupplierNumber(NewPacket.PacketID)
            if NewPacket.DataOrParity() not in ['Data', 'Parity']:
                dhnio.Dprint(2, "restore.PacketCameIn ERROR %s is not Data or Parity" % NewPacket.BlockNumber())
                self.FailStop()
                return
            if NewPacket.DataOrParity() == 'Data':
                self.OnHandData[SupplierNumber] = True
                packetID = packetid.MakePacketID(self.BackupID, self.BlockNumber, SupplierNumber, 'Data')
            elif NewPacket.DataOrParity() == 'Parity':
                self.OnHandParity[SupplierNumber] = True
                packetID = packetid.MakePacketID(self.BackupID, self.BlockNumber, SupplierNumber, 'Parity')
            filename = os.path.join(settings.getLocalBackupsDir(), packetID)
            # either way the payload of packet is saved
            dhnio.WriteFile(filename, NewPacket.Payload)                
            dhnio.Dprint(6, "restore.PacketCameIn saved as " + filename)
            if self.EccMap.Fixable(self.OnHandData, self.OnHandParity):
                self.PacketsToBlock()
            if self.packetInCallback is not None:
                self.packetInCallback(self.BackupID, NewPacket)
            return
        elif state == 'exist':
            # this packet should be checked during next loop iteration 
            pass
        else:
            pass

    def PacketsToBlock(self):
        if self.AbortState:
            return
        
        self.LastAction = time.time()
        dhnio.Dprint(6, "restore.PacketsToBlock - starting - block " + str(self.BlockNumber))
        
        io_throttle.DeleteBackupRequests(self.BackupID + "-" + str(self.BlockNumber))
        
        filename = os.path.join(settings.getLocalBackupsDir(), "newblock-" + self.BackupID)

        raidread.raidread(filename, eccmap.CurrentName(), self.BackupID, self.BlockNumber)
        blockbits = dhnio.ReadBinaryFile(filename)
        splitindex = blockbits.index(":")
        lengthstring = blockbits[0:splitindex]
        try:
            datalength = int(lengthstring)                                  # real length before raidmake/ECC
            blockdata = blockbits[splitindex+1:splitindex+1+datalength]     # remove padding from raidmake/ECC
            newblock = dhnblock.Unserialize(blockdata)                        # convert to object
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
            reactor.callLater(0, self.RestoreComplete)
        else:
            reactor.callLater(0, self.StartNewBlock)


    # PREPRO - right now we fetch all the parities.
    # Could save bandwidth by only fetching needed ones.
    def StartNewBlock(self):
        if self.AbortState:
            return
        self.LastAction = time.time()
        self.BlockNumber += 1                               # current one we are putting together
        dhnio.Dprint(6, "restore.StartNewBlock " + str(self.BlockNumber))
        self.OnHandData = [False] * self.EccMap.datasegments
        self.OnHandParity = [False] * self.EccMap.paritysegments
        self.DoNeededRequests()


    def DoNeededRequests(self):
        packetsToRequest = self.GetPacketNeeds()

        if self.EccMap.Fixable(self.OnHandData, self.OnHandParity):
            # dhnio.Dprint(2, "restore.StartNewBlock We have enough data to make block " + str(self.BlockNumber))
            reactor.callLater(0, self.PacketsToBlock)
            
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
            PacketID = packetid.MakePacketID(self.BackupID, self.BlockNumber, SupplierNumber, 'Data')
            # if os.path.exists(os.path.join(tmpfile.subdir('data-par'), PacketID)):
            if os.path.exists(os.path.join(settings.getLocalBackupsDir(), PacketID)):
                self.OnHandData[SupplierNumber] = True
            else:
                packetsToRequest.append(PacketID)
                
        for SupplierNumber in range(self.EccMap.paritysegments):
            PacketID = packetid.MakePacketID(self.BackupID, self.BlockNumber, SupplierNumber, 'Parity')
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
        if not self.Done:
            if self.AbortState:
                self.CloseWithAbort()
                return
            
            # if we've not done anything in last 60 seconds 
            # (no requests, no incoming, no block rebuilds), 
            # make sure we're on track)
            if time.time() - self.LastAction > 60:
                reactor.callLater(0, self.DoNeededRequests)
                
            reactor.callLater(self.PollTime, self.MonitorLoop)
            

    def FailStop(self):  # when we have an error in the restore, stop
        dhnio.Dprint(1, "restore.FailStop ERROR - new block does not look good")
        self.File.close()
        self.Done = True
        io_throttle.DeleteBackupRequests(self.BackupID + "-")
        self.MyDeferred.errback(self.BackupID+" Bad Block!!!")
        events.notify('restore', '%s failed to restore block number %d' % (self.BackupID, self.BlockNumber))


    def RestoreComplete(self):
        dhnio.Dprint(2, "restore.RestoreComplete - restore has finished. All is well that ends well!.")
        self.File.close()
        self.Done = True
        io_throttle.DeleteBackupRequests(self.BackupID + "-")
        self.MyDeferred.callback(self.BackupID+' done')
        events.info('restore', '%s restored successfully' % self.BackupID)


    def CloseWithAbort(self):
        dhnio.Dprint(4, "restore.CloseWithAbort " + self.BackupID)
        self.File.close()
        self.Done = True
        io_throttle.DeleteBackupRequests(self.BackupID + "-")
        self.MyDeferred.callback(self.BackupID+' aborted')
        events.info('restore', '%s restoring were aborted' % self.BackupID)


    def Abort(self): # for when user clicks the Abort restore button on the gui
        dhnio.Dprint(4, "restore.Abort " + self.BackupID)
        self.AbortState = True

