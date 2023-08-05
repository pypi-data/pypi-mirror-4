#!/usr/bin/python
#block_rebuilder.py
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2012
#    Use of this software constitutes acceptance of the Terms of Use
#      http://datahaven.net/terms_of_use.html
#    All rights reserved.
#

import os
import sys
import time
import random


try:
    from twisted.internet import reactor
except:
    sys.exit('Error initializing twisted.internet.reactor in block_rebuilder.py')

from twisted.internet.defer import Deferred, maybeDeferred
from twisted.internet import threads


import lib.dhnio as dhnio
import lib.misc as misc
import lib.nameurl as nameurl
import lib.transport_control as transport_control
import lib.settings as settings
import lib.contacts as contacts
import lib.eccmap as eccmap
import lib.tmpfile as tmpfile
import lib.diskspace as diskspace
from lib.automat import Automat


import fire_hire
import backup_rebuilder
import list_files_orator 
import lib.automats as automats

import backups
import raidread
import customerservice
import io_throttle
import backup_db
import contacts_status

_BlockRebuilder = None

#------------------------------------------------------------------------------ 

def A(event=None, arg=None):
    global _BlockRebuilder
    if _BlockRebuilder is None:
        _BlockRebuilder = BlockRebuilder()
    if event is not None:
        _BlockRebuilder.automat(event, arg)
    return _BlockRebuilder


class BlockRebuilder(Automat):
    timers = {'timer-1min':     (60,    ['REQUEST',]),
              'timer-1sec':     (1,     ['REQUEST', 'SENDING']),}
    
    def __init__(self,  
                 eccMap, 
                 backupID, 
                 blockNum, 
                 supplierSet, 
                 remoteData, 
                 remoteParity,
                 localData, 
                 localParity, 
                 creatorId = None, 
                 ownerId = None):
        self.eccMap = eccMap
        self.backupID = backupID
        self.blockNum = blockNum
        self.supplierSet = supplierSet
        self.supplierCount = len(self.supplierSet.suppliers)
        self.remoteData = remoteData
        self.remoteParity = remoteParity
        self.localData = localData
        self.localParity = localParity
        self.creatorId = creatorId
        self.ownerId = ownerId
        # at some point we may be dealing with when we're scrubbers
        if self.creatorId == None:
            self.creatorId = misc.getLocalID()
        if self.ownerId == None:
            self.ownerId = misc.getLocalID()
        # this files we want to rebuild
        # need to identify which files to work on
        self.missingData = [0] * self.supplierCount
        self.missingParity = [0] * self.supplierCount
        # list of packets ID we requested
        self.requestedFilesList = []
        # list of files to be send
        self.outstandingFilesList = []
        # time when we start sending files
        self.sendingStartedTime = 0
        # timeout to send a single file to supplier,
        # *2 because we want to be sure that it is not handled by io_throttle - it counts timeout too
        self.timeoutSending = 2 * int(settings.PacketSizeTarget() / settings.SendingSpeedLimit())
        # 1 if we sent a Data file to single supplier, 2 if get Ack from him, 3 if it was failed   
        self.dataSent = [0] * self.supplierCount
        # same for Parity files
        self.paritySent = [0] * self.supplierCount
        # for every packet we sending - remember if it was success or failed  
        self.sentReports = {}
        # dhnio.Dprint(8, 'block_rebuilder._BlockRebuilder blockNum=%s remote:{%s %s} local:{%s %s}' % (self.blockNum, self.remoteData, self.remoteParity, self.localData, self.localParity))
        Automat.__init__(self, 'block_rebuilder', 'AT_STARTUP', 10)
        
    def state_changed(self, oldstate, newstate):
        backup_rebuilder.A('block_rebuilder.state', newstate)
    
    def A(self, event, arg):
        #---AT_STARTUP---
        if self.state == 'AT_STARTUP':
            if event == 'start':
                self.doIdentifyMissingFiles()
                self.state = 'MISSING'
        #---MISSING---
        elif self.state == 'MISSING':
            if event == 'missing-files-identified' and not self.isMissingFilesOnHand():
                self.doRequestMissingFiles()
                self.state = 'REQUEST'
            elif event == 'missing-files-identified' and self.isMissingFilesOnHand():
                self.doRebuild()
                self.state = 'REBUILDING'
        #---REQUEST---
        elif self.state == 'REQUEST':
            if not self.isStopped() and ( ( event == 'timer-1sec' and self.isAllFilesReceived() ) or event == 'timer-1min' ):
                self.doRebuild()
                self.state = 'REBUILDING'
            elif event == 'timer-1sec' and self.isStopped():
                self.doDestroyMe()
                self.state = 'STOPPED'
        #---REBUILDING---
        elif self.state == 'REBUILDING':
            if event == 'rebuilding-finished' and self.isOutstandingFiles():
                self.doSendOutstandingFiles()
                self.state = 'SENDING'
            elif event == 'rebuilding-finished' and not self.isOutstandingFiles():
                self.doDestroyMe()
                self.state = 'FINISHED'
        #--SENDING---
        elif self.state == 'SENDING':
            if event == 'file-sent-report' and self.isAllFilesSent():
                self.doRemoveBlockFiles()
                self.doWorkDoneReport()
                self.doDestroyMe()
                self.state = 'DONE'
            elif event == 'timer-1sec' and self.isStopped():
                self.doWorkDoneReport()
                self.doDestroyMe()
                self.state = 'STOPPED'
            elif event == 'timer-1sec' and self.isTimeoutSending():
                self.doUpdateSentReports()
                self.doWorkDoneReport()
                self.doDestroyMe()
                self.state = 'TIMEOUT'
        #---FINISHED---
        elif self.state == 'FINISHED':
            pass
        #---STOPPED---
        elif self.state == 'STOPPED':
            pass
        #---DONE---
        elif self.state == 'DONE':
            pass
        #---TIMEOUT---
        elif self.state == 'TIMEOUT':
            pass
        
        
    def isStopped(self):
        return backup_rebuilder.ReadStoppedFlag()
    
    def isMissingFilesOnHand(self):
        for supplierNum in range(self.supplierCount):
            # if supplier do not have the Data but is on line 
            if self.missingData[supplierNum] == 1:
                # ... and we also do not have the Data 
                if self.localData[supplierNum] != 1:
                    # return False - will need request the file   
                    return False
            # same for Parity                
            if self.missingParity[supplierNum] == 1:
                if self.localParity[supplierNum] != 1:
                    return False
        #dhnio.Dprint(8, 'block_rebuilder.isMissingFilesOnHand return True')
        return True
        
    def isAllFilesReceived(self):
        return len(self.requestedFilesList) == 0
    
    def isAllFilesSent(self):
        return ( 1 not in self.dataSent ) and ( 1 not in self.paritySent )
    
    def isOutstandingFiles(self):
        return len(self.outstandingFilesList) > 0
    
    def isTimeoutSending(self):
        result = time.time() - self.sendingStartedTime > self.timeoutSending
        if result:
            dhnio.Dprint(6, 'block_rebuilder.isTimeoutSending return True, timeout=%d' % self.timeoutSending)
        return result
    
    def doIdentifyMissingFiles(self):
        def do_identify():
            self.availableSuppliers = self.supplierSet.GetActiveArray()
            for supplierNum in range(self.supplierCount):
                if self.availableSuppliers[supplierNum] == 0:
                    continue
                # if remote Data file not exist and supplier is online
                # we mark it as missing and will try to rebuild this file and send to him
                if self.remoteData[supplierNum] != 1:
                    # mark file as missing  
                    self.missingData[supplierNum] = 1
                # same for Parity file
                if self.remoteParity[supplierNum] != 1:
                    self.missingParity[supplierNum] = 1
            return True
        maybeDeferred(do_identify).addCallback(
            lambda x: self.automat('missing-files-identified'))
        
    def doRequestMissingFiles(self):
        self.availableSuppliers = self.supplierSet.GetActiveArray()
        # at the moment I'm download
        # everything I have available and needed
        for supplierNum in range(self.supplierCount):
            # if supplier is not alive - we can't request from him           
            if self.availableSuppliers[supplierNum] == 0:
                continue
            supplierID = self.supplierSet.suppliers[supplierNum]      
            # if the remote Data exist and is available because supplier is on line,
            # but we do not have it on hand - do request  
            if self.remoteData[supplierNum] == 1 and self.localData[supplierNum] == 0:
                PacketID = self.BuildFileName(supplierNum, 'Data')
                io_throttle.QueueRequestFile(self.FileReceived, self.creatorId, PacketID, self.ownerId, supplierID)
                self.requestedFilesList.append(PacketID)
            # same for Parity
            if self.remoteParity[supplierNum] == 1 and self.localParity[supplierNum] == 0:
                PacketID = self.BuildFileName(supplierNum, 'Parity')
                io_throttle.QueueRequestFile(self.FileReceived, self.creatorId, PacketID, self.ownerId, supplierID)
                self.requestedFilesList.append(PacketID)
        
    def doRebuild(self):
#        threads.deferToThread(self.AttemptRepair).addCallback(
#            lambda x: self.automat('rebuilding-thread-finished'))
        maybeDeferred(self.AttemptRebuild).addCallback(
            lambda x: self.automat('rebuilding-finished'))
        
    def doSendOutstandingFiles(self):
        for FileName, PacketID, supplierNum in self.outstandingFilesList:
            self.SendFile(FileName, PacketID, supplierNum)
        del self.outstandingFilesList
        self.outstandingFilesList = [] 
        self.sendingStartedTime = time.time()

    def doDestroyMe(self):
        automats.get_automats_by_index().pop(self.index)
        reactor.callLater(0, backup_rebuilder.RemoveBlockRebuilder, self)
    
    def doRemoveBlockFiles(self):
        # we want to remove files for this block 
        # because we only need them during rebuilding
        if settings.getGeneralLocalBackups() is True:
            # if user set this in settings - he want to keep the local files
            return
        # ... user do not want to keep local backups
        if settings.getGeneralWaitSuppliers() is True:
            # but he want to be sure - all suppliers are green for long time
            if contacts_status.hasOfflineSuppliers() or time.time() - fire_hire.GetLastFireTime() < 24*60*60:
                # some people are not there or we do not have stable team yet.
                # do not remove the files because we need it to rebuild
                return
        dhnio.Dprint(2, 'block_rebuilder.doRemoveBlockFiles [%s] [%s]' % (self.remoteData, self.remoteParity))
        for supplierNum in range(self.supplierCount):
            # data_filename = os.path.join(tmpfile.subdir('data-par'), self.BuildFileName(supplierNum, 'Data'))
            # parity_filename = os.path.join(tmpfile.subdir('data-par'), self.BuildFileName(supplierNum, 'Parity'))
            data_filename = os.path.join(settings.getLocalBackupsDir(), self.BuildFileName(supplierNum, 'Data'))
            parity_filename = os.path.join(settings.getLocalBackupsDir(), self.BuildFileName(supplierNum, 'Parity'))
            if os.path.isfile(data_filename) and self.remoteData[supplierNum] == 1:
                try:
                    os.remove(data_filename)
                    #dhnio.Dprint(6, '    ' + os.path.basename(data_filename))
                except:
                    dhnio.DprintException()
            if os.path.isfile(parity_filename) and self.remoteParity[supplierNum] == 1:
                try:
                    os.remove(parity_filename)
                    #dhnio.Dprint(6, '    ' + os.path.basename(parity_filename))
                except:
                    dhnio.DprintException()
        
    def doWorkDoneReport(self):
        if backup_rebuilder.ReadStoppedFlag() is False:
            backups.RebuildReport(self.backupID, self.blockNum, self.remoteData, self.remoteParity, self.sentReports)

    def doUpdateSentReports(self):
        for supplierNum in range(self.supplierCount):
            if self.dataSent[supplierNum] == 1:
                packetID = self.BuildFileName(supplierNum, 'Data')
                self.sentReports[packetID] = 'timeout2' 
                dhnio.Dprint(6, 'block_rebuilder.doUpdateSentReports %s' % packetID)
            if self.paritySent[supplierNum] == 1:
                packetID = self.BuildFileName(supplierNum, 'Parity')
                self.sentReports[packetID] = 'timeout2' 
                dhnio.Dprint(6, 'block_rebuilder.doUpdateSentReports %s' % packetID)
             
    #------------------------------------------------------------------------------ 

    def HaveAllData(self, parityMap):
        for segment in parityMap:
            if self.localData[segment] == 0:
                return False
        return True


    def AttemptRebuild(self):
        #dhnio.Dprint(6, 'block_rebuilder.AttemptRepair BEGIN')
        madeProgress = True
        while madeProgress:
            madeProgress = False
            # will check all data packets we have 
            for supplierNum in range(self.supplierCount):
                dataFileName = self.BuildRaidFileName(supplierNum, 'Data')
                # if we do not have this item on hands - we will reconstruct it from other items 
                if self.localData[supplierNum] == 0:
                    parityNum, parityMap = self.eccMap.GetDataFixPath(self.localData, self.localParity, supplierNum)
                    if parityNum != -1:
                        rebuildFileList = []
                        rebuildFileList.append(self.BuildRaidFileName(parityNum, 'Parity'))
                        for supplierParity in parityMap:
                            if supplierParity != supplierNum:
                                rebuildFileList.append(self.BuildRaidFileName(supplierParity, 'Data'))
                        raidread.RebuildOne(rebuildFileList, len(rebuildFileList), dataFileName)
                    #send the rebuilt file back, set the missing to zero
                    if os.path.exists(dataFileName):
                        self.localData[supplierNum] = 1
                        madeProgress = True
                        dhnio.Dprint(8, 'block_rebuilder.AttemptRebuild made progress with supplier %d' % supplierNum)
                # now we check again if we have the data on hand after rebuild at it is missing - send it
                # but also check to not duplicate sending to this man            
                if self.localData[supplierNum] == 1 and self.missingData[supplierNum] == 1 and self.dataSent[supplierNum] == 0:
                    dhnio.Dprint(8, "block_rebuilder.AttemptRebuild new outstanding Data for supplier %d" % supplierNum)
                    self.outstandingFilesList.append((dataFileName, self.BuildFileName(supplierNum, 'Data'), supplierNum))
                    self.dataSent[supplierNum] = 1
        # now with parities ...            
        for supplierNum in range(self.supplierCount):
            parityFileName = self.BuildRaidFileName(supplierNum, 'Parity')
            if self.localParity[supplierNum] == 0:
                parityMap = self.eccMap.ParityToData[supplierNum]
                if self.HaveAllData(parityMap):
                    rebuildFileList = []
                    for supplierParity in parityMap:
                        rebuildFileList.append(self.BuildRaidFileName(supplierParity, 'Data'))
                    raidread.RebuildOne(rebuildFileList, len(rebuildFileList), parityFileName)
                    if os.path.exists(parityFileName):
                        dhnio.Dprint(8, 'block_rebuilder.AttemptRebuild parity file found after rebuilding for supplier %d' % supplierNum)
                        self.localParity[supplierNum] = 1
            # so we have the parity on hand and it is missing - send it
            if self.localParity[supplierNum] == 1 and self.missingParity[supplierNum] == 1 and self.paritySent[supplierNum] == 0:
                dhnio.Dprint(8, 'block_rebuilder.AttemptRebuild new outstanding Parity for supplier %d' % supplierNum)
                self.outstandingFilesList.append((parityFileName, self.BuildFileName(supplierNum, 'Parity'), supplierNum))
                self.paritySent[supplierNum] = 1
        return True


    def SendFile(self, FileName, PacketID, supplierNum):
        io_throttle.QueueSendFile(FileName, 
                                  PacketID, 
                                  self.supplierSet.suppliers[supplierNum], 
                                  self.ownerId, 
                                  self.SendFileAcked, 
                                  self.SendFileFailed,)
        dhnio.Dprint(8, "block_rebuilder.SendFile to supplier %d" % supplierNum)


    def SendFileAcked(self, packet, remoteID, packetID):
        dhnio.Dprint(8, 'block_rebuilder.SendFileAcked to %s with %s' % (nameurl.GetName(remoteID), packetID))
        try:
            backupID, blockNum, supplierNum, dataORparity = packetID.split("-")
            blockNum = int(blockNum)
            supplierNum = int(supplierNum)
            if dataORparity == 'Data':
                self.missingData[supplierNum] = 0
                self.remoteData[supplierNum] = 1
                self.dataSent[supplierNum] = 2
            elif dataORparity == 'Parity':
                self.missingParity[supplierNum] = 0
                self.remoteParity[supplierNum] = 1
                self.paritySent[supplierNum] = 2
            else:
                dhnio.Dprint(8, "block_rebuilder.SendFileAcked WARNING odd PacketID? -" + str(packetID))
            if self.sentReports.has_key(packetID):
                dhnio.Dprint(2, 'block_rebuilder.SendFileAcked WARNING already got sending report for %s' % packetID)
            self.sentReports[packetID] = 'acked'
        except:
            dhnio.DprintException()
        self.automat('file-sent-report')


    def SendFileFailed(self, creatorID, packetID, reason):
        dhnio.Dprint(8, 'block_rebuilder.SendFileFailed to %s with %s (%s)' % (nameurl.GetName(creatorID), packetID, reason))
        try:
            backupID, blockNum, supplierNum, dataORparity = packetID.split("-")
            blockNum = int(blockNum)
            supplierNum = int(supplierNum)
            if dataORparity == 'Data':
                self.missingData[supplierNum] = 1
                self.remoteData[supplierNum] = 0
                self.dataSent[supplierNum] = 3
            elif dataORparity == 'Parity':
                self.missingParity[supplierNum] = 1
                self.remoteParity[supplierNum] = 0
                self.paritySent[supplierNum] = 3
            else:
                dhnio.Dprint(8, "block_rebuilder.SendFileFailed WARNING odd PacketID? -" + str(packetID))
            if self.sentReports.has_key(packetID):
                dhnio.Dprint(2, 'block_rebuilder.SendFileFailed WARNING already got sending report for %s' % packetID)
            self.sentReports[packetID] = reason
        except:
            dhnio.DprintException()
        self.automat('file-sent-report')


    def FileReceived(self, packet):
        try:
            self.requestedFilesList.remove(packet.PacketID)
        except:
            dhnio.DprintException()
            return
        # filename = os.path.join(tmpfile.subdir('data-par'), packet.PacketID)
        filename = os.path.join(settings.getLocalBackupsDir(), packet.PacketID)
        if packet.Valid():
            dhnio.Dprint(8, "block_rebuilder.FileReceived %s,  requestedFilesList length is %d" % (packet.PacketID, len(self.requestedFilesList)))
            # if we managed to rebuild a file 
            # before a request came in don't overwrite it
            if os.path.exists(filename):
                dhnio.Dprint(4, "block_rebuilder.FileReceived WARNING file already existed " + filename)
                try: 
                    os.remove(filename)
                except:
                    dhnio.DprintException()
            dhnio.WriteFile(filename, packet.Payload)
            try: 
                supplierNum = int((packet.PacketID.split("-"))[2])
                if packet.PacketID.endswith("-Data"):
                    self.localData[supplierNum] = 1
                elif packet.PacketID.endswith("-Parity"):
                    self.localParity[supplierNum] = 1
            except:
                dhnio.DprintException()              
        else:
            # TODO 
            # if we didn't get a valid packet ... re-request it or delete it?
            dhnio.Dprint(8, "block_rebuilder.FileReceived WARNING" + filename + " not valid")
            try: 
                os.remove(filename)
            except:
                dhnio.DprintException()
            #io_throttle.QueueRequestFile(self.FileReceived, misc.getLocalID(), packet.PacketID, self.ownerId, packet.RemoteID)


    def BuildRaidFileName(self, supplierNumber, dataOrParity):
        # return os.path.join(tmpfile.subdir('data-par'), self.BuildFileName(supplierNumber, dataOrParity))
        return os.path.join(settings.getLocalBackupsDir(), self.BuildFileName(supplierNumber, dataOrParity))


    def BuildFileName(self, supplierNumber, dataOrParity):
        return self.backupID + "-" + str(self.blockNum) + "-" + str(supplierNumber) + "-" + dataOrParity

#------------------------------------------------------------------------------ 
