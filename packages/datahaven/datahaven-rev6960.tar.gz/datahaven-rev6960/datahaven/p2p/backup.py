#!/usr/bin/python
#backup.py
#
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2012
#    Use of this software constitutes acceptance of the Terms of Use
#      http://datahaven.net/terms_of_use.html
#    All rights reserved.
#
#
#  This interfaces between a pipe from something like tar and the twisted code
#    for rest of DataHaven.NET
#  We see how many packets are waiting to be sent,
#    and if it is not too many, and we can make more, we make some more.
#
#  Main idea:
#     1) When a backup is started a backup object is created
#     2) We get a file descriptor for the process creating the tar archive
#     3) We always use select/poll before reading so we never block
#     4) We also poll to see if more needed.
#     5) We number/name blocks so can be sure what is what when we read back later
#     6) We call raidmake to split block and make parities
#     7) We put parts into dhnpackets and give these to transport_control


import os
import sys
import time
import cStringIO
import gc


try:
    from twisted.internet import reactor
except:
    sys.exit('Error initializing twisted.internet.reactor in backup.py')

from twisted.internet import threads
from twisted.internet.defer import Deferred, maybeDeferred


import lib.dhnio as dhnio
import lib.misc as misc
import lib.dhnpacket as dhnpacket
import lib.contacts as contacts
import lib.commands as commands
import lib.settings as settings
import lib.packetid as packetid
import lib.nonblocking as nonblocking
import lib.eccmap as eccmap
import lib.dhncrypto as dhncrypto
import lib.tmpfile as tmpfile
from lib.automat import Automat


import lib.automats as automats
import fire_hire
import contacts_status

import raidmake
import dhnblock
import io_throttle
import events
import backup_db


#-------------------------------------------------------------------------------

class backup(Automat):
    timers = {'timer-01sec':    (0.1, ['RUN', 'READ']), 
              'timer-1sec':     (1, ['SENDING'])}
    
    def __init__(self, backupID, pipe, blockSize=None, resultDeferred=None):
        self.backupID = backupID
        self.eccmap = eccmap.Current()
        self.pipe = pipe
        self.blockSize = blockSize
        if self.blockSize is None:
            self.blockSize = self.eccmap.nodes() * settings.PacketSizeTarget()
        self.ask4abort = False
        self.stateEOF = False
        self.stateReading = False
        #self.currentBlockData = ''
        self.currentBlockData = cStringIO.StringIO()
        self.currentBlockSize = 0
        self.blockNumber = 0
        self.dataSent = 0
        self.blocksSent = 0
        self.closed = False
        self.sendingDelay = 0.1
        self.result = ''
        if resultDeferred is None:
            self.resultDefer = Deferred()
        else:
            self.resultDefer = resultDeferred
        self.packetResultCallback = None
        # need to give time for supplier to receive the packet
        # but do not wait too long because other suppliers receive same data faster
        # this is a number of seconds we give to supplier to receive our packet
        self.PacketFailedTimeout = int(settings.PacketSizeTarget() / settings.SendingSpeedLimit())
        # (packetID, filename) queue for each supplier by his number
        # [suplierNumber](packetID, filename)
        self.outstandingPackets = {}
        # (packetID, filename) that is currently sending for every supplier number
        self.currentlySendingPackets = {} 
        # time when we start sending the packet for each supplier by his number    
        self.sendingBeginTimers = {}
        # how many packets was failed to send for each supplier by his number
        self.sentFailedCounts = {} 
        # failed and success packets for each block by its number
        # store both data and parity packets in this form
        # [blockNumber]['D','P'][success, failed]      
        self.blocksResultDict = {}
        # timed out packets list for each supplier by his number
        self.timedOutPackets = {}
        # (total bytes sent, total duration sending) to each supplier by his number
        # we count only time "during sending packet",
        # this starts from moment of start sending single packet 
        # and moment when we receive an ack on this packet 
        self.sendingStats = {}
        Automat.__init__(self, 'backup', 'AT_STARTUP', 10)
        self.automat('init')
        events.info('backup', 'backup %s started' % self.backupID)
        dhnio.Dprint(6, 'backup.__init__ %s %s %d %d' % (self.backupID, self.eccmap, self.blockSize, self.PacketFailedTimeout))
        
    def A(self, event, arg):
        #---AT_STARTUP---
        if self.state == 'AT_STARTUP':
            if event == 'init':
                self.doStartProcessOutgoingFiles()
                self.state = 'RUN'
        #---RUN---
        elif self.state == 'RUN':
            if event == 'timer-01sec' and self.isAborted():
                self.doClose()
                self.doReport()
                self.doDestroyMe()
                self.state = 'ABORTED'
            elif event == 'timer-01sec' and not self.isAborted():
                self.state = 'READ'
        #---READ---
        elif self.state == 'READ':
            if event == 'timer-01sec' and self.isPipeReady() and not self.isEOF() and not self.isReadingNow() and not self.isBlockReady():
                self.doRead()
            elif event == 'timer-01sec' and not self.isReadingNow() and (self.isBlockReady() or self.isEOF()):
                self.doBlock()
                self.state = 'BLOCK'
        #---BLOCK---
        elif self.state == 'BLOCK':
            if event == 'block-ready':
                self.doRaid(arg)
                self.state = 'RAID'
        #---RAID---
        elif self.state == 'RAID':
            if event == 'raid-done' and not self.isEOF():
                self.doSend(arg)
                self.doNewBlock()
                self.state = 'RUN'
            elif event == 'raid-done' and self.isEOF():
                self.doSend(arg)
                self.state = 'SENDING'
        #---SENDING---
        elif self.state == 'SENDING':
            if event == 'timer-1sec' and self.isSentAll():
                self.doClose()
                self.doReport()
                self.doDestroyMe()
                self.state = 'DONE'
            elif event == 'timer-1sec' and self.isAborted():
                self.doClose()
                self.doReport()
                self.doDestroyMe()
                self.state = 'ABORTED'
        #---DONE---
        elif self.state == 'DONE':
            pass
        #---ABORTED---
        elif self.state == 'ABORTED':
            pass

    def isAborted(self):
        return self.ask4abort
         
    def isSentAll(self):
        return len(self.blocksResultDict) == 0 and self.dataSent > 0
    
    def isPipeReady(self):
        return self.pipe is not None and self.pipe.state() in [nonblocking.PIPE_CLOSED, nonblocking.PIPE_READY2READ]
    
    def isBlockReady(self):
        return self.currentBlockSize >= self.blockSize
    
    def isEOF(self):
        return self.stateEOF
    
    def isReadingNow(self):
        return self.stateReading

    def doClose(self):
        self.closed = True
        
    def doDestroyMe(self):
        self.currentBlockData.close()
        del self.currentBlockData
        automats.get_automats_by_index().pop(self.index)
        reactor.callLater(0, backup_db.RemoveRunningBackupObject, self.backupID)
        collected = gc.collect()
        dhnio.Dprint(6, 'backup.doDestroyMe collected %d objects' % collected)

    def doReport(self):
        if self.result == '':
            self.resultDefer.callback(self.backupID)
            events.info('backup', 'backup %s done successfully' % self.backupID)
        elif self.result == 'abort':  
            self.resultDefer.callback(self.backupID+' abort')
            events.info('backup', 'backup %s was aborted' % self.backupID)
        else:
            self.resultDefer.errback(self.backupID)
            dhnio.Dprint(1, 'backup.doReport ERROR %s result is [%s]' % (self.backupID, self.result))
            events.info('backup', 'backup %s failed: %s' % (self.backupID, self.result))

    def doRead(self):
        def readChunk():
            size = self.blockSize - self.currentBlockSize
            if size < 0:
                dhnio.Dprint(1, "backup.readChunk ERROR eccmap.nodes=" + str(self.eccmap.nodes()))
                dhnio.Dprint(1, "backup.readChunk ERROR blockSize=" + str(self.blockSize))
                dhnio.Dprint(1, "backup.readChunk ERROR currentBlockSize=" + str(self.currentBlockSize))
                raise Exception('size < 0, blockSize=%s, currentBlockSize=%s' % (self.blockSize, self.currentBlockSize))
                return ''
            elif size == 0:
                return ''
            if self.pipe is None:
                raise Exception('backup.pipe is None')
                return ''
            if self.pipe.state() == nonblocking.PIPE_CLOSED:
                dhnio.Dprint(4, 'backup.readChunk the state is PIPE_CLOSED !!!!!!!!!!!!!!!!!!!!!!!!')
                return ''
            if self.pipe.state() == nonblocking.PIPE_READY2READ:
                newchunk = self.pipe.recv(size)
                if newchunk == '':
                    dhnio.Dprint(4, 'backup.readChunk pipe.recv() returned empty string')
                return newchunk
            dhnio.Dprint(1, "backup.readChunk ERROR pipe.state=" + str(self.pipe.state()))
            raise Exception('backup.pipe.state is ' + str(self.pipe.state()))
            return ''
        def readDone(data):
            #self.currentBlockData += data
            self.currentBlockData.write(data)
            self.currentBlockSize += len(data)
            self.stateReading = False
            if data == '':
                self.stateEOF = True
            #dhnio.Dprint(12, 'backup.readDone %d bytes' % len(data))
        self.stateReading = True
        maybeDeferred(readChunk).addCallback(readDone)

    def doBlock(self):
        def _doBlock():
            dhnio.Dprint(12, 'backup.doBlock blockNumber=%d size=%d atEOF=%s' % (self.blockNumber, self.currentBlockSize, self.stateEOF))
            #src = self.currentBlockData
            src = self.currentBlockData.getvalue()
            #self.currentBlockData.close()
            #del self.currentBlockData
            ret = dhnblock.dhnblock(
                misc.getLocalID(),
                self.backupID,
                self.blockNumber,
                dhncrypto.NewSessionKey(),
                dhncrypto.SessionKeyType(),
                self.stateEOF,
                src,)
            del src
            return ret
        maybeDeferred(_doBlock).addCallback(
            lambda block: self.automat('block-ready', block),)

    def doRaid(self, arg):
        newblock = arg
        dhnio.Dprint(8, 'backup.doRaid block=%d size=%d eof=%s ' % (
            self.blockNumber, self.currentBlockSize, str(self.stateEOF),))
        fileno, filename = tmpfile.make('backup')
        serializedblock = newblock.Serialize()
        blocklen = len(serializedblock)
        os.write(fileno, str(blocklen) + ":" + serializedblock)
        os.close(fileno)
        threads.deferToThread(raidmake.raidmake, 
                              filename, 
                              self.eccmap.name, 
                              self.backupID, 
                              self.blockNumber).addBoth(
                                  lambda outDir: self.automat('raid-done', newblock))
        del serializedblock

    def doSend(self, arg):
        newblock = arg
        for supplierNum in range(self.eccmap.nodes()):
            # we do all data then all parity
            for DataOrParity in ('Data','Parity'):
                if not self.outstandingPackets.has_key(supplierNum):
                    self.outstandingPackets[supplierNum] = []
                packetId = newblock.BackupID + '-' + str(newblock.BlockNumber) + '-' + str(supplierNum) + '-' + DataOrParity
                # fullfilename = os.path.join(tmpfile.subdir('data-par'), packetId)
                fullfilename = os.path.join(settings.getLocalBackupsDir(), packetId)
                self.outstandingPackets[supplierNum].append((packetId, fullfilename))
        # self.dataSent += len(self.currentBlockData)
        self.dataSent += self.currentBlockSize
        del newblock

    def doNewBlock(self):
        #self.currentBlockData = ''
        self.currentBlockData.close()
        del self.currentBlockData
        self.currentBlockData = cStringIO.StringIO()
        self.currentBlockSize = 0
        self.blockNumber += 1
        if self.packetResultCallback is not None:
            self.packetResultCallback(self.backupID, None)
        
    def doStartProcessOutgoingFiles(self):
        reactor.callLater(0, self.processSending)     
        
    #------------------------------------------------------------------------------ 

    def processSending(self):
        if self.closed:
            return
        if len(self.outstandingPackets) > 0:
            self.sendingDelay = 0.1
        else:
            if self.sendingDelay < 4.0:
                self.sendingDelay *= 2.0
        # let's check all outstanding packets for all suppliers
        for supplierNum in self.outstandingPackets.keys():
            # if nothing to send for this supplier - skip
            if len(self.outstandingPackets[supplierNum]) == 0:
                continue
            # if we already sending a file to this man
            # need to check how long we are doing this
            beginSendingTime = self.sendingBeginTimers.get(supplierNum, None)
            if beginSendingTime is not None:
                if time.time() - beginSendingTime < self.PacketFailedTimeout:
                    # currently sending to the supplier - check next supplier
                    continue
                dhnio.Dprint(6, 'backup.processSending timeout sending for supplier %d' % supplierNum)
                # so this packet is timed out
                # and we increase failed counter for this man
                if not self.sentFailedCounts.has_key(supplierNum):
                    self.sentFailedCounts[supplierNum] = 0
                self.sentFailedCounts[supplierNum] += 1
                # remove this packet from currently sending packets
                timedOutPacketID, filename = self.currentlySendingPackets.pop(supplierNum) 
                # now we want to mark this packet as timed out
                # so when packetAcked or packetFailed will be fired by io_throttle
                # we will check and do not update block result 
                if not self.timedOutPackets.has_key(supplierNum):
                    self.timedOutPackets[supplierNum] = []
                self.timedOutPackets[supplierNum].append(timedOutPacketID)
                # remove this timer because we know now that packet is failed
                self.sendingBeginTimers.pop(supplierNum)
                # finally update block result 
                self.blockResult(timedOutPacketID, False)
            # now we know we did not sending to this supplier
            # and there are some files to be sent to him, take one from his queue
            packetId, fullfilename = self.outstandingPackets[supplierNum].pop(0)
            # if we already have 2 failed packets sent to this man
            # we do not want to send any more, because no trust to him
            # backup_monitor will reconstruct this backup later
            if self.sentFailedCounts.has_key(supplierNum):
                #dhnio.Dprint(6, 'backup.processSending supplier %d failed counts is %d' % (supplierNum, self.sentFailedCounts[supplierNum]))
                if self.sentFailedCounts[supplierNum] >= 2:
                    self.blockResult(packetId, False)
                    continue
            # do sending  
            io_throttle.QueueSendFile(
                fullfilename,
                packetId,
                contacts.getSupplierID(supplierNum),
                misc.getLocalID(),
                self.packetAcked,
                self.packetFailed,)
            # save current packetId and filename
            self.currentlySendingPackets[supplierNum] = (packetId, fullfilename) 
            # remember current time for this supplier
            self.sendingBeginTimers[supplierNum] = time.time()
            #dhnio.Dprint(6, 'backup.processSending begin sending [%s] to supplier %d' % (packetId, supplierNum))
        # call again later
        # attenuation
        reactor.callLater(self.sendingDelay, self.processSending)


    def packetAcked(self, packet, ownerID, packetID):
        if self.closed:
            return
        # take supplier number ...
        supplierNum = int(packetID.split('-')[2])
        # if packet is timed out - skip
        if self.timedOutPackets.has_key(supplierNum):
            if packetID in self.timedOutPackets[supplierNum]:
                # but remove it from this list to be smart
                self.timedOutPackets[supplierNum].remove(packetID)
                return
        # ... and remove from currently sending packets
        currentPacketID, filename = self.currentlySendingPackets.pop(supplierNum)
        if packetID != currentPacketID:
            raise Exception('incorrect packetID=%s for supplier %d, currentlySendingPackets=%s' % (packetID, supplierNum, self.currentlySendingPackets))
        # and also remove timer so we know that supplier is free and able to receive next packet
        startTimePacket = self.sendingBeginTimers.pop(supplierNum)
        # increase amount of total bytes sent to this man
        # supplier puts number of received bytes in the Ack
        # and we know how much he received in last packet of Data     
        if not self.sendingStats.has_key(supplierNum):
            self.sendingStats[supplierNum] = [0, 0]
        self.sendingStats[supplierNum][0] += int(packet.Payload)
        # remember the period of time how long we sent this packet
        self.sendingStats[supplierNum][1] += time.time() - startTimePacket
        # now we can remove the local file because remote supplier got it and ...
        if settings.getGeneralLocalBackups() is False:
            # ... user do not want to keep local backups
            if settings.getGeneralWaitSuppliers() is True:
                # but he want to be sure - all suppliers are green for long time
                if time.time() - fire_hire.GetLastFireTime() > 24*60*60:
                    # that is fine - we know those people for long. they are trusted.
                    # now we do not need local file
                    # fullfilename = os.path.join(tmpfile.subdir('data-par'), packetID)
                    fullfilename = os.path.join(settings.getLocalBackupsDir(), packetID)
                    if os.path.isfile(fullfilename):
                        dhnio.Dprint(2, 'backup.packetAcked will remove [%s]' % fullfilename)
                        try:
                            os.remove(fullfilename)
                        except:
                            dhnio.DprintException()
        # update block result finally
        self.blockResult(packetID, True)
        # update GUI
        if self.packetResultCallback is not None:
            self.packetResultCallback(self.backupID, packet)
        #dhnio.Dprsint(10, 'backup.packetAcked [%s] outstanding=%d' % (packetID, len(self.outstanding)))


    def packetFailed(self, creatorID, packetID, why):
        if self.closed:
            return
        # take supplier number ...
        supplierNum = int(packetID.split('-')[2])
        #dhnio.Dprint(6, 'backup.packetFailed [%s] for supplier %d' % (packetID, supplierNum))
        # if packet is timed out - skip
        if self.timedOutPackets.has_key(supplierNum):
            if packetID in self.timedOutPackets[supplierNum]:
                # but remove it from this list to be smart
                self.timedOutPackets[supplierNum].remove(packetID)
                return
        # ... and remove from currently sending packets
        currentPacketID, filename = self.currentlySendingPackets.pop(supplierNum)
        if packetID != currentPacketID:
            raise Exception('incorrect packetID=%s for supplier %d, currentlySendingPackets=%s' % (packetID, supplierNum, self.currentlySendingPackets))
        # and also remove timer so we know that supplier is free and able to receive next packet
        startTime = self.sendingBeginTimers.pop(supplierNum)
        # increase failed counter
        if not self.sentFailedCounts.has_key(supplierNum):
            self.sentFailedCounts[supplierNum] = 0
        self.sentFailedCounts[supplierNum] += 1
        # update block result finally
        self.blockResult(packetID, False)
        # do notify gui
        if self.packetResultCallback is not None:
            self.packetResultCallback(self.backupID, None)


    def blockResult(self, PacketID, Result):
        backupID, blockNum, supplierNum, dataORparity  = PacketID.split('-')
        blockNum = int(blockNum)
        supplierNum = int(supplierNum)
        DorP = dataORparity[0] # "D" or "P"
        if not self.blocksResultDict.has_key(blockNum):
            self.blocksResultDict[blockNum] = {'D': [0, 0], 'P': [0, 0]}
        self.blocksResultDict[blockNum][DorP][int(Result)] += 1
        succesData = self.blocksResultDict[blockNum]['D'][1]
        failedData = self.blocksResultDict[blockNum]['D'][0]
        succesParity = self.blocksResultDict[blockNum]['P'][1]
        failedParity = self.blocksResultDict[blockNum]['P'][0]
        if succesData + failedData >= self.eccmap.nodes() and succesParity + failedParity >= self.eccmap.nodes():
            self.blocksResultDict.pop(blockNum)
            self.blocksSent += 1
            if succesData < self.eccmap.DataNeeded():
                dhnio.Dprint(4, 'backup.blockResult WARNING block %d-Data keeps only %d suppliers from %d!' % (
                    blockNum, succesData, self.eccmap.nodes()))
            if succesParity < self.eccmap.DataNeeded():
                dhnio.Dprint(4, 'backup.blockResult WARNING block %d-Parity keeps only %d suppliers from %d!' % (
                    blockNum, succesParity, self.eccmap.nodes()))
            dhnio.Dprint(6, 'backup.blockResult %d data[%d/%d] parity[%d/%d] %d more blocks' % (
                blockNum, succesData, self.eccmap.nodes(), succesParity, self.eccmap.nodes(), len(self.blocksResultDict)))


    def abort(self):
        dhnio.Dprint(4, 'backup.abort id='+str(self.backupID))
        self.ask4abort = True
        self.result = 'abort'


    def SetPacketResultCallback(self, cb):
        self.packetResultCallback = cb
        
    def GetStats(self):
        return self.sendingStats 
        


