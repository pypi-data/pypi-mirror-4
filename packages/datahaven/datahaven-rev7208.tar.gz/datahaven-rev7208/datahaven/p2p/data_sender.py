#!/usr/bin/python
#data_sender.py
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2012
#    Use of this software constitutes acceptance of the Terms of Use
#      http://datahaven.net/terms_of_use.html
#    All rights reserved.
#

import os
import sys

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
    timers = {'timer-5min':     (60*5,     ['READY']),
              'timer-1sec':     (2,        ['SENDING'])}

    def state_changed(self, oldstate, newstate):
        automats.set_global_state('DATASEND ' + newstate)

    def A(self, event, arg):
        #---AT_STARTUP---
        if self.state is 'AT_STARTUP':
            if event == 'init' :
                self.state = 'READY'
        #---READY---
        elif self.state is 'READY':
            if event == 'new-data' or event == 'timer-5min' or event == 'restart' :
                self.doScanAndQueue(arg)
                self.state = 'SCAN_BLOCKS'
        #---SCAN_BLOCKS---
        elif self.state is 'SCAN_BLOCKS':
            if event == 'scan-done' and self.isQueueEmpty(arg) :
                self.state = 'READY'
            elif event == 'scan-done' and not self.isQueueEmpty(arg) :
                self.state = 'SENDING'
        #---SENDING---
        elif self.state is 'SENDING':
            if event == 'restart' or ( ( event == 'block-acked' or event == 'block-failed' ) and self.isQueueEmpty(arg) ) :
                self.doScanAndQueue(arg)
                self.state = 'SCAN_BLOCKS'
            elif event == 'timer-1sec' :
                self.doPrintStats(arg)

    def isQueueEmpty(self, arg):
        return io_throttle.IsSendingQueueEmpty()
    
    def doScanAndQueue(self, arg):
        dhnio.Dprint(6, 'data_sender.doScanAndQueue')
        for backupID in misc.sorted_backup_ids(backups.local_files().keys()):
            packetsBySupplier = backups.ScanBlocksToSend(backupID)
            for supplierNum in packetsBySupplier.keys():
                supplier_idurl = contacts.getSupplierID(supplierNum)
                if not supplier_idurl:
                    dhnio.Dprint(2, 'data_sender.doScanAndQueue WARNING ?supplierNum? %s for %s' % (packetID, backupID))
                    continue
                if not io_throttle.OkToSend(supplier_idurl):
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
                    filename = os.path.join(settings.getLocalBackupsDir(), packetID)
                    io_throttle.QueueSendFile(
                        filename, 
                        packetID, 
                        supplier_idurl, 
                        misc.getLocalID(), 
                        self.packetAcked, 
                        self.packetFailed)
                    # dhnio.Dprint(6, '  %s for %s' % (packetID, backupID))
        self.automat('scan-done')
        
    def doPrintStats(self, arg):
        if dhnio.Debug(9):
            transfers = transport_control.current_transfers()
            bytes_stats = transport_control.current_bytes_transferred()
            s = ''
            for info in transfers:
                s += '%s ' % (diskspace.MakeStringFromBytes(bytes_stats[info.transfer_id]).replace(' ', '').replace('bytes', 'b'))
            dhnio.Dprint(0, 'transfers: ' + s[:120])

    def packetAcked(self, packet, ownerID, packetID):
        backupID, blockNum, supplierNum, dataORparity = packetid.BidBnSnDp(packetID)
        backups.RemoteFileReport(backupID, blockNum, supplierNum, dataORparity, True)
        self.automat('block-acked', packetID)
    
    def packetFailed(self, remoteID, packetID, why):
        backupID, blockNum, supplierNum, dataORparity = packetid.BidBnSnDp(packetID)
        backups.RemoteFileReport(backupID, blockNum, supplierNum, dataORparity, False)
        self.automat('block-failed', packetID)
    
    
        
        
        
        
        
        
        
        

