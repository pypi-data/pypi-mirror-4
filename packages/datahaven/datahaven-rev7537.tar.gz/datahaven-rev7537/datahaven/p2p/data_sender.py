#!/usr/bin/python
#data_sender.py
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2013
#    Use of this software constitutes acceptance of the Terms of Use
#      http://datahaven.net/terms_of_use.html
#    All rights reserved.
#

import os
import sys
import time

try:
    from twisted.internet import reactor
except:
    sys.exit('Error initializing twisted.internet.reactor in data_sender.py')

import lib.dhnio as dhnio
import lib.misc as misc
import lib.packetid as packetid
import lib.contacts as contacts
import lib.settings as settings
import lib.diskspace as diskspace
import lib.nameurl as nameurl
import lib.transport_control as transport_control
import lib.automat as automat
import lib.automats as automats

import io_throttle
import backups
import fire_hire
import contact_status
import backup_monitor

_DataSender = None

#------------------------------------------------------------------------------ 

def A(event=None, arg=None):
    global _DataSender
    if _DataSender is None:
        _DataSender = DataSender('data_sender', 'READY', 6)
    if event is not None:
        _DataSender.automat(event, arg)
    return _DataSender


class DataSender(automat.Automat):
    timers = {'timer-30min':     (60*30,     ['READY']),
              # 'timer-1sec':     (2,        ['SENDING'])
              }

    def state_changed(self, oldstate, newstate):
        automats.set_global_state('DATASEND ' + newstate)

    def A(self, event, arg):
        #---READY---
        if self.state is 'READY':
            if event == 'new-data' or event == 'timer-30min' or event == 'restart' :
                self.state = 'SCAN_BLOCKS'
                self.doScanAndQueue(arg)
            elif event == 'init' :
                pass
        #---SCAN_BLOCKS---
        elif self.state is 'SCAN_BLOCKS':
            if event == 'scan-done' and self.isQueueEmpty(arg) :
                self.state = 'READY'
                self.doRemoveUnusedFiles(arg)
                backup_monitor.A('restart')
            elif event == 'scan-done' and not self.isQueueEmpty(arg) :
                self.state = 'SENDING'
        #---SENDING---
        elif self.state is 'SENDING':
            if event == 'restart' or ( ( event == 'block-acked' or event == 'block-failed' ) and self.isQueueEmpty(arg) ) :
                self.state = 'SCAN_BLOCKS'
                self.doScanAndQueue(arg)
            elif event == 'timer-1sec' :
                self.doPrintStats(arg)

    def isQueueEmpty(self, arg):
        return io_throttle.IsSendingQueueEmpty()
    
#    def isMoreDataToTransfer(self, arg):
#        for backupID in backups.GetBackupIds():
#            for blockNum in range(backups.GetKnownMaxBlockNum(backupID) + 1):
#                remoteArray = {'Data':   backups.GetRemoteDataArray(backupID, blockNum),
#                               'Parity': backups.GetRemoteParityArray(backupID, blockNum)}
#                localArray =  {'Data':   backups.GetLocalDataArray(backupID, blockNum),
#                               'Parity': backups.GetLocalParityArray(backupID, blockNum)}
#                for supplierNum in range(len(remoteArray)):
#                    for DP in ['Data', 'Parity']:
#                        if remoteArray[DP][supplierNum] != 1 and localArray[DP][supplierNum] == 1:
#                            return True
#        return False 
    
    def doScanAndQueue(self, arg):
        dhnio.Dprint(6, 'data_sender.doScanAndQueue')
        for backupID in misc.sorted_backup_ids(backups.local_files().keys()):
            packetsBySupplier = backups.ScanBlocksToSend(backupID)
            for supplierNum in packetsBySupplier.keys():
                supplier_idurl = contacts.getSupplierID(supplierNum)
                if not supplier_idurl:
                    dhnio.Dprint(2, 'data_sender.doScanAndQueue WARNING ?supplierNum? %s for %s' % (supplierNum, backupID))
                    continue
                for packetID in packetsBySupplier[supplierNum]:
                    backupID_, blockNum, supplierNum_, dataORparity = packetid.BidBnSnDp(packetID)
                    if backupID_ != backupID:
                        dhnio.Dprint(2, 'data_sender.doScanAndQueue WARNING ?backupID? %s for %s' % (packetID, backupID))
                        continue
                    if supplierNum_ != supplierNum:
                        dhnio.Dprint(2, 'data_sender.doScanAndQueue WARNING ?supplierNum? %s for %s' % (packetID, backupID))
                        continue
                    if io_throttle.HasPacketInSendQueue(supplier_idurl, packetID):
                        continue
                    if not io_throttle.OkToSend(supplier_idurl):
                        continue
                    if len(transport_control.transfers_by_idurl(supplier_idurl)) > 0:
                        continue
                    filename = os.path.join(settings.getLocalBackupsDir(), packetID)
                    if not os.path.isfile(filename):
                        continue
                    io_throttle.QueueSendFile(
                        filename, 
                        packetID, 
                        supplier_idurl, 
                        misc.getLocalID(), 
                        self.packetAcked, 
                        self.packetFailed)
                    # dhnio.Dprint(6, '  %s for %s' % (packetID, backupID))
        self.automat('scan-done')
        
#        dhnio.Dprint(2, 'data_sender.doRemoveUnusedFiles [%s] [%s]' % (self.remoteData, self.remoteParity))
#        for supplierNum in range(self.supplierCount):
#            # data_filename = os.path.join(tmpfile.subdir('data-par'), self.BuildFileName(supplierNum, 'Data'))
#            # parity_filename = os.path.join(tmpfile.subdir('data-par'), self.BuildFileName(supplierNum, 'Parity'))
#            data_filename = os.path.join(settings.getLocalBackupsDir(), self.BuildFileName(supplierNum, 'Data'))
#            parity_filename = os.path.join(settings.getLocalBackupsDir(), self.BuildFileName(supplierNum, 'Parity'))
#            if os.path.isfile(data_filename) and self.remoteData[supplierNum] == 1:
#                try:
#                    os.remove(data_filename)
#                    #dhnio.Dprint(6, '    ' + os.path.basename(data_filename))
#                except:
#                    dhnio.DprintException()
#            if os.path.isfile(parity_filename) and self.remoteParity[supplierNum] == 1:
#                try:
#                    os.remove(parity_filename)
#                    #dhnio.Dprint(6, '    ' + os.path.basename(parity_filename))
#                except:
#                    dhnio.DprintException()

    def doPrintStats(self, arg):
        if dhnio.Debug(12):
            transfers = transport_control.current_transfers()
            bytes_stats = transport_control.current_bytes_transferred()
            s = ''
            for info in transfers:
                s += '%s ' % (diskspace.MakeStringFromBytes(bytes_stats[info.transfer_id]).replace(' ', '').replace('bytes', 'b'))
            dhnio.Dprint(0, 'transfers: ' + s[:120])

    def doRemoveUnusedFiles(self, arg):
        # we want to remove files for this block 
        # because we only need them during rebuilding
        if settings.getGeneralLocalBackups() is True:
            # if user set this in settings - he want to keep the local files
            return
        # ... user do not want to keep local backups
        if settings.getGeneralWaitSuppliers() is True:
            # but he want to be sure - all suppliers are green for long time
            if contact_status.hasOfflineSuppliers() or time.time() - fire_hire.GetLastFireTime() < 24*60*60:
                # some people are not there or we do not have stable team yet
                # do not remove the files because we need it to rebuild
                return 
        dhnio.Dprint(6, 'data_sender.doRemoveUnusedFiles')
        for backupID in misc.sorted_backup_ids(backups.local_files().keys()):
            packets = backups.ScanBlocksToRemove(backupID, settings.getGeneralWaitSuppliers())
            for packetID in packets:
                filename = os.path.join(settings.getLocalBackupsDir(), packetID)
                if os.path.isfile(filename):
                    try:
                        os.remove(filename)
                        dhnio.Dprint(6, '    ' + os.path.basename(filename))
                    except:
                        dhnio.DprintException()
        backups.ReadLocalFiles()
                         

    def packetAcked(self, packet, ownerID, packetID):
        backupID, blockNum, supplierNum, dataORparity = packetid.BidBnSnDp(packetID)
        backups.RemoteFileReport(backupID, blockNum, supplierNum, dataORparity, True)
        self.automat('block-acked', packetID)
    
    def packetFailed(self, remoteID, packetID, why):
        backupID, blockNum, supplierNum, dataORparity = packetid.BidBnSnDp(packetID)
        backups.RemoteFileReport(backupID, blockNum, supplierNum, dataORparity, False)
        self.automat('block-failed', packetID)
    
    
        
        
        
        
        
        
        
        

