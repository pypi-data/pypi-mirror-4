#!/usr/bin/python
#backups.py
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2012
#    All rights reserved.
#

import os
import sys
import time
import random
import gc


try:
    from twisted.internet import reactor
except:
    sys.exit('Error initializing twisted.internet.reactor in backups.py')

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


import backup_monitor
import backup_rebuilder  
import fire_hire
import list_files_orator
import lib.automats as automats

import raidread
import customerservice
import io_throttle
import backup_db
import contacts_status

#------------------------------------------------------------------------------ 

_RemoteFiles = {}
_LocalFiles = {}
_RemoteMaxBlockNumbers = {}
_LocalMaxBlockNumbers = {}
_LocalBackupSize = {}
_BackupsInProcess = []
_SuppliersSet = None
_BackupStatusNotifyCallback = None
_StatusCallBackForGuiBackup = None
_LocalFilesNotifyCallback = None
_UpdatedBackupIDs = set()
_RepaintingTask = None   
_RepaintingTaskDelay = 0.1  

#------------------------------------------------------------------------------ 

def init():
    dhnio.Dprint(4, 'backups.init')
    RepaintingProcess(True)
    ReadLocalFiles()
    ReadLatestRawListFiles()


def shutdown():
    dhnio.Dprint(4, 'backups.shutdown')
    RepaintingProcess(False)

#------------------------------------------------------------------------------ 

# index for all remote files (on suppliers HDD's) stored in dictionary
# values are 0 or 1 - this mean file exist or not 
# all entries are indexed by [backupID][blockNum]['D' or 'P'][supplierNum]
def remote_files():
    global _RemoteFiles
    return _RemoteFiles


# max block number for every remote backup ID
def remote_max_block_numbers():
    global _RemoteMaxBlockNumbers
    return _RemoteMaxBlockNumbers


# index for all local files (on our HDD) stored in dictionary
# values are 0 or 1 - this mean file exist or not 
# all entries are indexed by [backupID][blockNum]['D' or 'P'][supplierNum]
def local_files():
    global _LocalFiles
    return _LocalFiles


# max block number for every local backup ID
def local_max_block_numbers():
    global _LocalMaxBlockNumbers
    return _LocalMaxBlockNumbers


def local_backup_size():
    global _LocalBackupSize
    return _LocalBackupSize


# currently working backups (started from dobackup.py)
def backups_in_process():
    global _BackupsInProcess
    return _BackupsInProcess


def suppliers_set():
    global _SuppliersSet
    if _SuppliersSet is None:
        _SuppliersSet = SuppliersSet(contacts.getSupplierIDs())
    return _SuppliersSet


#------------------------------------------------------------------------------ 
# this should represent the set of suppliers for either the user or for a customer the user
# is acting as a scrubber for
class SuppliersSet:
    def __init__(self, supplierList):
        self.suppliers = [] 
        self.supplierCount = 0 
        self.successPackets = {}
        self.failedPackets = {}
        self.failedSuppliers = set()
        self.UpdateSuppliers(supplierList)

    def GetActiveArray(self):
        activeArray = [0] * self.supplierCount
        for i in range(self.supplierCount):
            if contacts_status.isOnline(self.suppliers[i]):
                activeArray[i] = 1
            else:
                activeArray[i] = 0
        return activeArray

    def ChangedArray(self, supplierList):
        changedArray = [0] * self.supplierCount
        changedIdentities = []
        for i in range(self.supplierCount):
            if supplierList[i] != self.suppliers[i]:
                changedArray[i] = 1
                changedIdentities.append(supplierList[i])
        return changedArray, changedIdentities

    def SuppliersChanged(self, supplierList):
        if len(supplierList) != self.supplierCount:
            return True
        for i in range(self.supplierCount):
            if supplierList[i] != self.suppliers[i]:
                return True
        return False

    # if suppliers 1 and 3 changed, return [1,3]
    def SuppliersChangedNumbers(self, supplierList):
        changedList = []
        for i in range(self.supplierCount):
            if supplierList[i] != self.suppliers[i]:
                changedList.append(i)
        return changedList

    def SupplierCountChanged(self, supplierList):
        if len(supplierList) != self.supplierCount:
            return True
        else:
            return False

    def UpdateSuppliers(self, supplierList):
        self.suppliers = supplierList
        self.supplierCount = len(self.suppliers)
        self.successPackets.clear()
        self.failedPackets.clear()
        for supplierNum in range(self.supplierCount):
            self.successPackets[supplierNum] = 0
            self.failedPackets[supplierNum] = 0
        self.failedSuppliers.clear()

#------------------------------------------------------------------------------ 

def IncomingListFiles(supplierNum, packet, listFileText):
    supplierIdentity = packet.OwnerID
    #self.requestedListFilesPacketIDs.discard(supplierIdentity)
    #dhnio.Dprint(8, 'backups.IncomingListFiles for supplier %d other requests: %s' % (supplierNum, self.requestedListFilesPacketIDs))

    if supplierNum >= suppliers_set().supplierCount:
        dhnio.Dprint(2, 'backups.IncomingListFiles WARNING incorrect supplier number %d, number of suppliers is %d' % (supplierNum, suppliers_set().supplierCount))
        return

    backups2remove = ReadRawListFiles(supplierNum, listFileText)
    list_files_orator.IncommingListFiles(supplierNum, packet, listFileText)
    SaveLatestRawListFiles(supplierIdentity, listFileText)
    if len(backups2remove) > 0:
        customerservice.RequestDeleteListBackups(backups2remove)


def ReadRawListFiles(supplierNum, listFileText):
    backups2remove = []
    # new code            
    # examples:
    # F20090709034221PM-0-Data from 0-1000
    # F20090709034221PM-0-Data from 0-1000 missing 1,3,
    for line in listFileText.splitlines():
        line = line.strip()
        # comment lines in Files reports start with blank,
        if line == '':
            continue
        # also don't consider the identity a backup,
        if line.find('http://') != -1 or line.find('.xml') != -1:
            continue
        # nor the backup_info.xml
        if line == settings.BackupInfoFileName():
            continue
        words = line.split(' ')
        # minimum is 3 words: "F20090709034221PM-0-Data", "from", "0-1000"
        if len(words) < 3:
            dhnio.Dprint(2, 'backups.ReadRawListFiles WARNING incorrect line:[%s]' % line)
            continue
        try:
            backupID, lineSupplierNum, dataORparity = words[0].split('-')
            minBlockNum, maxBlockNum = words[2].split('-')
            lineSupplierNum = int(lineSupplierNum)
            maxBlockNum = int(maxBlockNum)
        except:
            dhnio.Dprint(2, 'backups.ReadRawListFiles WARNING incorrect line:[%s]' % line)
            continue
        if backupID == '':
            dhnio.Dprint(2, 'backups.ReadRawListFiles WARNING incorrect line:[%s]' % line)
            continue
        if dataORparity not in ['Data', 'Parity']:
            dhnio.Dprint(2, 'backups.ReadRawListFiles WARNING incorrect line:[%s]' % line)
            continue
        if lineSupplierNum != supplierNum:
            # this mean supplier have old files and we do not need it 
            # TODO what to do...  remove the files? Send "DeleteFile" packet?
            backups2remove.append(backupID)
            continue
        if backup_db.IsDeleted(backupID):
            backups2remove.append(backupID)
            continue
        missingBlocksSet = set()
        if len(words) ==  5:
            if words[3].strip() != 'missing':
                dhnio.Dprint(2, 'backups.ReadRawListFiles WARNING incorrect line:[%s]' % line)
                continue
            missingBlocksSet = set(words[4].split(','))
        if not remote_files().has_key(backupID):
            remote_files()[backupID] = {}
            dhnio.Dprint(6, 'backups.ReadRawListFiles new remote entry for %s created in the memory' % backupID)
        # +1 because range(2) give us [0,1] but we want [0,1,2]
        for blockNum in range(maxBlockNum+1):
            if not remote_files()[backupID].has_key(blockNum):
                remote_files()[backupID][blockNum] = {
                    'D': [0] * suppliers_set().supplierCount,
                    'P': [0] * suppliers_set().supplierCount,}
            # we set -1 if the file is missing and 1 if exist, so 0 mean "no info yet" ... smart!
            bit = -1 if str(blockNum) in missingBlocksSet else 1 
            if dataORparity == 'Data':
                remote_files()[backupID][blockNum]['D'][supplierNum] = bit
            elif dataORparity == 'Parity':
                remote_files()[backupID][blockNum]['P'][supplierNum] = bit
        # save max block number for this backup
        if not remote_max_block_numbers().has_key(backupID):
            remote_max_block_numbers()[backupID] = -1 
        if maxBlockNum > remote_max_block_numbers()[backupID]:
            remote_max_block_numbers()[backupID] = maxBlockNum
        
        # mark this backup to be repainted
        RepaintBackup(backupID)
    # return list of backupID's which is too old but stored on suppliers machines 
    return backups2remove
            

def SaveLatestRawListFiles(idurl, listFileText):
    supplierPath = settings.SupplierPath(idurl)
    if not os.path.isdir(supplierPath):
        try:
            os.makedirs(supplierPath)
        except:
            dhnio.DprintException()
    dhnio.WriteFile(settings.SupplierListFilesFilename(idurl), listFileText)


def ReadLatestRawListFiles():
    dhnio.Dprint(4, 'backups.ReadLatestRawListFiles')
    for idurl in contacts.getSupplierIDs():
        filename = os.path.join(settings.SupplierPath(idurl, 'listfiles'))
        if os.path.isfile(filename):
            listFileText = dhnio.ReadTextFile(filename)
            if listFileText.strip() != '':
                ReadRawListFiles(contacts.numberForSupplier(idurl), listFileText)


def ScanMissingBlocks(backupID):
    missingBlocks = set()
    localMaxBlockNum = local_max_block_numbers().get(backupID, -1)
    remoteMaxBlockNum = remote_max_block_numbers().get(backupID, -1)
    supplierActiveArray = suppliers_set().GetActiveArray()
    #dhnio.Dprint(6, 'backups.ScanMissingBlocks supplierActiveArray=%s' % supplierActiveArray)

    if not remote_files().has_key(backupID):
        if not local_files().has_key(backupID):
            # we have no local and no remote info for this backup
            # no chance to do some rebuilds...
            # TODO but how we get here ?! 
            dhnio.Dprint(4, 'backups.ScanMissingBlocks no local and no remote info for %s' % backupID)
        else:
            # we have no remote info, but some local files exists
            # so let's try to sent all of them
            # need to scan all block numbers 
            for blockNum in range(localMaxBlockNum):
                # we check for Data and Parity packets
                localData = GetLocalDataArray(backupID, blockNum)
                localParity = GetLocalParityArray(backupID, blockNum)  
                for supplierNum in range(len(supplierActiveArray)):
                    # if supplier is not alive we can not send to him
                    # so no need to scan for missing blocks 
                    if supplierActiveArray[supplierNum] != 1:
                        continue
                    if localData[supplierNum] == 1:
                        missingBlocks.add(blockNum)
                    if localParity[supplierNum] == 1:
                        missingBlocks.add(blockNum)
    else:
        # now we have some remote info
        # we take max block number from local and remote
        maxBlockNum = max(remoteMaxBlockNum, localMaxBlockNum)
        # dhnio.Dprint(6, 'backups.ScanMissingBlocks maxBlockNum=%d' % maxBlockNum)
        # and increase by one because range(3) give us [0, 1, 2], but we want [0, 1, 2, 3]
        for blockNum in range(maxBlockNum + 1):
            # if we have few remote files, but many locals - we want to send all missed 
            if not remote_files()[backupID].has_key(blockNum):
                missingBlocks.add(blockNum)
                continue
            # take remote info for this block
            remoteData = GetRemoteDataArray(backupID, blockNum)
            remoteParity = GetRemoteParityArray(backupID, blockNum)  
            # now check every our supplier for every block
            for supplierNum in range(len(supplierActiveArray)):
                # if supplier is not alive we can not send to him
                # so no need to scan for missing blocks 
                if supplierActiveArray[supplierNum] != 1:
                    continue
                if remoteData[supplierNum] != 1:    # -1 means missing
                    missingBlocks.add(blockNum)     # 0 - no info yet
                if remoteParity[supplierNum] != 1:  # 1 - file exist on remote supplier 
                    missingBlocks.add(blockNum)
                
    # dhnio.Dprint(6, 'backups.ScanMissingBlocks %s' % missingBlocks)
    return list(missingBlocks)


def ReadLocalFiles():
    global _LocalFilesNotifyCallback
    local_files().clear()
    local_max_block_numbers().clear()
    local_backup_size().clear()
    counter = 0
    # for filename in os.listdir(tmpfile.subdir('data-par')):
    for filename in os.listdir(settings.getLocalBackupsDir()):
        if filename.startswith('newblock-'):
            continue
        try:
            backupID, blockNum, supplierNum, dataORparity  = filename.split('-')
            blockNum = int(blockNum)
            supplierNum = int(supplierNum)
        except:
            dhnio.Dprint(4, 'backups.ReadLocalFiles WARNING incorrect filename ' + filename)
            continue
        if dataORparity not in ['Data', 'Parity']:
            dhnio.Dprint(4, 'backups.ReadLocalFiles WARNING Data or Parity? ' + filename)
            continue
        if supplierNum >= suppliers_set().supplierCount:
            dhnio.Dprint(4, 'backups.ReadLocalFiles WARNING supplier number %d > %d %s' % (supplierNum, suppliers_set().supplierCount, filename))
            continue
        if not local_files().has_key(backupID):
            local_files()[backupID] = {}
            dhnio.Dprint(6, 'backups.ReadLocalFiles new local entry for %s created in the memory' % backupID)
        if not local_files()[backupID].has_key(blockNum):
            local_files()[backupID][blockNum] = {
                'D': [0] * suppliers_set().supplierCount,
                'P': [0] * suppliers_set().supplierCount}
        local_files()[backupID][blockNum][dataORparity[0]][supplierNum] = 1
        if not local_max_block_numbers().has_key(backupID):
            local_max_block_numbers()[backupID] = -1
        if local_max_block_numbers()[backupID] < blockNum:
            local_max_block_numbers()[backupID] = blockNum
        if not local_backup_size().has_key(backupID):
            local_backup_size()[backupID] = 0
        # local_backup_size()[backupID] += os.path.getsize(os.path.join(tmpfile.subdir('data-par'), filename))
        try:
            local_backup_size()[backupID] += os.path.getsize(os.path.join(settings.getLocalBackupsDir(), filename))
        except:
            dhnio.DprintException()
        counter += 1
    dhnio.Dprint(6, 'backups.ReadLocalFiles  %d files indexed' % counter)
    if dhnio.Debug(6):
        try:
            if sys.version_info >= (2, 6):
                #localSZ = sys.getsizeof(local_files())
                #remoteSZ = sys.getsizeof(remote_files())
                import lib.getsizeof
                localSZ = lib.getsizeof.total_size(local_files())
                remoteSZ = lib.getsizeof.total_size(remote_files())
                dhnio.Dprint(6, '    all local info uses %d bytes in the memory' % localSZ)
                dhnio.Dprint(6, '    all remote info uses %d bytes in the memory' % remoteSZ)
        except:
            dhnio.DprintException()
    if _LocalFilesNotifyCallback is not None:
        _LocalFilesNotifyCallback()


def SetSupplierList(supplierList):
    # going from 2 to 4 suppliers (or whatever) invalidates all backups
    # all suppliers was changed because its number was changed
    # so we lost everything!
    if len(supplierList) != suppliers_set().supplierCount:
        dhnio.Dprint(2, "backups.SetSupplierList got list of %d suppliers, but we have %d now!" % (len(supplierList), suppliers_set().supplierCount))
        # erase all remove info
        #remote_files() = {}
        remote_files().clear()
        remote_max_block_numbers().clear()
        # also erase local info
        #local_files() = {}
        local_files().clear()
        local_max_block_numbers().clear()
        local_backup_size().clear()
        # new ecc map will be taken later
        #self.eccMap = None
        # remove all local files and all backups
        DeleteAllBackups()
        # restart backup_monitor
        backup_monitor.Restart()
    # only single suppliers changed
    # need to erase info only for them 
    elif suppliers_set().SuppliersChanged(supplierList):
        # take a list of suppliers positions that was changed
        changedSupplierNums = suppliers_set().SuppliersChangedNumbers(supplierList)
        # notify io_throttle that we do not neeed already this suppliers
        for supplierNum in changedSupplierNums:
            dhnio.Dprint(2, "backups.SetSupplierList supplier %d changed: [%s]->[%s]" % (
                supplierNum, nameurl.GetName(suppliers_set().suppliers[supplierNum]), nameurl.GetName(supplierList[supplierNum])))
            io_throttle.DeleteSuppliers([suppliers_set().suppliers[supplierNum]])
        # remove remote info for this guys
        for backupID in remote_files().keys():
            for blockNum in remote_files()[backupID].keys():
                for supplierNum in changedSupplierNums:
                    remote_files()[backupID][blockNum]['D'][supplierNum] = 0
                    remote_files()[backupID][blockNum]['P'][supplierNum] = 0
        # restart backup_monitor
        backup_monitor.Restart()
    # finally save the list of current suppliers and clear all stats 
    suppliers_set().UpdateSuppliers(supplierList)


def RebuildReport(backupID, blockNum, remoteData, remoteParity, sentReports):
    if not remote_files().has_key(backupID):
        remote_files()[backupID] = {}
        dhnio.Dprint(6, 'backups.RebuildReport new remote entry for %s created in the memory' % backupID)
    if not remote_files()[backupID].has_key(blockNum):
        remote_files()[backupID][blockNum] = {
            'D': [0] * suppliers_set().supplierCount,
            'P': [0] * suppliers_set().supplierCount,}
    # save reconstructed block info into remote info structure, synchronize
    for supplierNum in range(suppliers_set().supplierCount):
        remote_files()[backupID][blockNum]['D'][supplierNum] = remoteData[supplierNum]
        remote_files()[backupID][blockNum]['P'][supplierNum] = remoteParity[supplierNum]
    # if we know only 5 blocks stored on remote machine
    # but we got reconstructed 6th block - remember this  
    remote_max_block_numbers()[backupID] = max(
        remote_max_block_numbers().get(backupID, -1),
        blockNum)
    
#    # remember sent results
#    for packetID, result in sentReports.items():
#        try:
#            backupID, blockNum, supplierNum, dataORparity = packetID.split("-")
#            blockNum = int(blockNum)
#            supplierNum = int(supplierNum)
#            supplierIDURL = suppliers_set().suppliers[supplierNum]
#            if result is 'acked':
#                suppliers_set().successPackets[supplierNum] += 1
#            else:
#                suppliers_set().failedPackets[supplierNum] += 1
#                if suppliers_set().failedPackets[supplierNum] >= 6:
#                    supplierIdentity = contacts.getContact(supplierIDURL)
#                    supplierContact = '' if supplierIdentity is None else supplierIdentity.getContact() 
#                    if not supplierContact.startswith('cspace://'):
#                        # mark this guy as failed if 6 times we were failed to sent to him
#                        suppliers_set().failedSuppliers.add(supplierIDURL)
#                        dhnio.Dprint(4, 'backups.RebuildReport %s have %d fails - mark him as failed' % (
#                            nameurl.GetName(supplierIDURL), suppliers_set().failedPackets[supplierNum]))
#                    else:
#                        # but if he is 'cspace' user - give him more chances - 24 times
#                        if suppliers_set().failedPackets[supplierNum] >= 24:
#                            suppliers_set().failedSuppliers.add(supplierIDURL)
#                            dhnio.Dprint(4, 'backups.RebuildReport %s is "cspace user" and have %d fails - mark him as failed' % (
#                                nameurl.GetName(supplierIDURL), suppliers_set().failedPackets[supplierNum]))
#                        
#        except:
#            dhnio.DprintException()

    # mark to repaint this backup in gui
    RepaintBackup(backupID)


def RepaintBackup(backupID): 
    global _UpdatedBackupIDs
    _UpdatedBackupIDs.add(backupID)


def RepaintingProcess(on_off):
    global _UpdatedBackupIDs
    global _BackupStatusNotifyCallback
    global _RepaintingTask
    global _RepaintingTaskDelay
    if on_off is False:
        _RepaintingTaskDelay = 0.5
        if _RepaintingTask is not None:
            if not _RepaintingTask.called:
                _RepaintingTask.cancel()
                _RepaintingTask = None
                _UpdatedBackupIDs.clear()
                return
    if len(_UpdatedBackupIDs) > 0:
        for backupID in _UpdatedBackupIDs:
            if _BackupStatusNotifyCallback is not None:
                _BackupStatusNotifyCallback(backupID)
        _UpdatedBackupIDs.clear()
        _RepaintingTaskDelay = 0.5
    else:
        if _RepaintingTaskDelay < 2.0:
            _RepaintingTaskDelay *= 2.0
    # attenuation
    _RepaintingTask = reactor.callLater(_RepaintingTaskDelay, RepaintingProcess, True)


# if there is a backup in process, one supplier may list more files in the backup than another,
# leading the backups to try to fix a backup in process.  We need to tell the backups
# when a backup is in process and when it is finished
def AddBackupInProcess(BackupName):
    backups_in_process().append(BackupName)


def RemoveBackupInProcess(BackupName):
    if BackupName in backups_in_process():
        backups_in_process().remove(BackupName)


def IsBackupInProcess(BackupID):
    return BackupID in backups_in_process()

#------------------------------------------------------------------------------ 
          
def DeleteAllBackups():
    for backupId in set(local_files().keys() + remote_files().keys()):
        DeleteBackup(backupId)
    DeleteAllLocalBackups()


# if the user deletes a backup, make sure we remove any work we're doing on it
def DeleteBackup(backupID, removeLocalFilesToo=True):
    dhnio.Dprint(4, 'backups.DeleteBackup ' + backupID)
    # abort backup if it just started and is running at the moment
    backup_db.AbortRunningBackup(backupID)
    # also remove from list of running backups  
    if backupID in backups_in_process():
        backups_in_process().remove(backupID)
    # if we have several copies of same ID in working queue - remove them all
    backup_rebuilder.RemoveBackupToWork(backupID)
    # if we requested for files for this backup - we do not need it anymore
    io_throttle.DeleteBackupRequests(backupID)
    # remove interests in transport_control
    transport_control.DeleteBackupInterest(backupID)
    # mark it as being deleted in the db
    backup_db.DeleteDirBackup(backupID)
    # finally remove local files for this backupID
    if removeLocalFilesToo:
        DeleteLocalBackupFiles(backupID)
    # remove all remote info for this backup from the memory 
    if remote_files().has_key(backupID):
        #del remote_files()[backupID]
        remote_files().pop(backupID)
        dhnio.Dprint(4, '  remote info for %s were removed from memory, other remote files:' % backupID)
        dhnio.Dprint(4, '  %s' % str(remote_files().keys()))
    if remote_max_block_numbers().has_key(backupID):
        del remote_max_block_numbers()[backupID]
    # also remove local info
    if local_files().has_key(backupID):
        #del local_files()[backupID]
        local_files().pop(backupID)
        dhnio.Dprint(4, '  local info for %s were removed from memory, other local files:' % backupID)
        dhnio.Dprint(4, '  %s' % str(local_files().keys()))
    if local_max_block_numbers().has_key(backupID):
        del local_max_block_numbers()[backupID]
    if local_backup_size().has_key(backupID):
        del local_backup_size()[backupID]


def DeleteAllSupplierData(supplierNum):
    io_throttle.DeleteSuppliers([suppliers_set().suppliers[supplierNum]])


def DeleteLocalBackupFiles(backupID):
    dhnio.Dprint(4, 'backups.DeleteLocalBackupFiles ' + backupID)
    num = 0
    sz = 0
    # localDir = tmpfile.subdir('data-par')
    localDir = settings.getLocalBackupsDir()
#    if backupID not in local_files():
#        local_files()[backupID] = {}
    for filename in os.listdir(localDir):
        if filename.startswith(backupID):
#            try:
#                backupID_, blockNum, supplierNum, dataORparity = filename.split("-")
#                blockNum = int(blockNum)
#                supplierNum = int(supplierNum)
#            except:
#                dhnio.DprintException()
#                continue
#            if backupID_ != backupID:
#                dhnio.Dprint(4, 'backups.DeleteLocalBackupFiles WARNING incorrect file name: %s' % filename)
#                continue
            filepath = os.path.join(localDir, filename)
            try:
                sz += os.path.getsize(filepath) 
                os.remove(filepath)
                num += 1
#                if dataORparity == 'Data':
#                    local_files()[backupID][blockNum]['D'][supplierNum] = 0
#                elif dataORparity == 'Parity':
#                    local_files()[backupID][blockNum]['P'][supplierNum] = 0
#                else:
#                    dhnio.Dprint(4, 'backups.DeleteLocalBackupFiles WARNING incorrect file name: %s' % filename)
            except:
                dhnio.Dprint(2, 'backups.DeleteLocalBackupFiles ERROR can not remove ' + filepath)
                dhnio.DprintException()
    local_files()[backupID] = []
    local_max_block_numbers()[backupID] = -1
    local_backup_size()[backupID] = 0
    return num, sz


def DeleteAllLocalBackups():
    dhnio.Dprint(4, 'backups.DeleteAllLocalBackups')
    num = 0
    sz = 0
    backupIDs = set()
    # localDir = tmpfile.subdir('data-par')
    localDir = settings.getLocalBackupsDir()
    for filename in os.listdir(localDir):
        filepath = os.path.join(localDir, filename)
        try:
            backupID, blockNum, supplierNum, dataORparity = filename.split("-")
            sz += os.path.getsize(filepath) 
            os.remove(filepath)
            num += 1
            backupIDs.add(backupID)
        except:
            dhnio.Dprint(1, 'backups.DeleteAllLocalBackups ERROR can not remove ' + filepath)
            dhnio.DprintException()
    dhnio.Dprint(4, 'backups.DeleteAllLocalBackups %d backups removed in %d files of total size %s' % (
        len(backupIDs), num, diskspace.MakeStringFromBytes(sz)))

#------------------------------------------------------------------------------ 

def GetListFilesBackupIds(supplierNum, supplierId, listFileText):
    rawlist = listFileText.splitlines()
    resultlist = []
    for line in rawlist:
        # comment lines in Files reports start with blank,
        # also don't consider the identity a backup,
        # nor the backup_info.xml
        if len(line) > 0 and (line[0] == ' ' or line.strip() == supplierId or line == settings.BackupInfoFileName()):
            continue
        dashindex = line.find("-")
        backupId = ''
        if dashindex>0: 
            # if this is supplier 3 make sure we have a -3-
            if line.find("-" + str(supplierNum) + "-") > 0:   
                # if there is a dash use only part before the dash
                backupId=line[0:dashindex]                    
        if backupId != '' and backupId not in resultlist:
            resultlist.append(backupId)
    return misc.sorted_backup_ids(resultlist)


# if we get a line "F20090709034221PM-0-Data from 0-1000"
# or "F20090709034221PM-0-Data from 0-1000 missing 1,3,"
# this will return 1000
def GetLineMaxBlockNum(line):
    try:
        maxBlock = -1
        workLine = line
        if line.find(" missing ") > 0:
            workLine = line[0:line.find(" missing ")]
        lineMax = int(workLine[workLine.rfind("-")+1:])
        if lineMax > maxBlock:
            maxBlock = lineMax
        return maxBlock
    except:
        return -1


def GetLineMissingBlocks(line, lineMax, backupMax):
    missingArray = []
    missingindex = line.find(" missing ") 
    if missingindex != -1:
        missingArray = line[missingindex+9:].split(",")
    if '' in missingArray:
        missingArray.remove('')
    if backupMax > lineMax:
        intMissingArray = range(lineMax+1,backupMax+1)
        for i in intMissingArray:
            missingArray.append(str(i))
    return missingArray


def GetBackupStats(backupID):
    if not remote_files().has_key(backupID):
        return 0, 0, [(0, 0)] * suppliers_set().supplierCount
    percentPerSupplier = 100.0 / suppliers_set().supplierCount
    # ??? maxBlockNum = remote_max_block_numbers().get(backupID, -1)
    maxBlockNum = GetKnownMaxBlockNum(backupID)
    fileNumbers = [0] * suppliers_set().supplierCount
    totalNumberOfFiles = 0
    for blockNum in remote_files()[backupID].keys():
        for supplierNum in range(len(fileNumbers)):
            if supplierNum < suppliers_set().supplierCount:
                if remote_files()[backupID][blockNum]['D'][supplierNum] == 1:
                    fileNumbers[supplierNum] += 1
                    totalNumberOfFiles += 1
                if remote_files()[backupID][blockNum]['P'][supplierNum] == 1:
                    fileNumbers[supplierNum] += 1
                    totalNumberOfFiles += 1
    statsArray = []
    for supplierNum in range(suppliers_set().supplierCount):
        if maxBlockNum > -1:
            # 0.5 because we count both Parity and Data.
            percent = percentPerSupplier * 0.5 * fileNumbers[supplierNum] / ( maxBlockNum + 1 )
        else:
            percent = 0.0
        statsArray.append(( percent, fileNumbers[supplierNum] ))
    del fileNumbers 
    return totalNumberOfFiles, maxBlockNum, statsArray

# return totalPercent, totalNumberOfFiles, totalSize, maxBlockNum, statsArray
def GetBackupLocalStats(backupID):
    # ??? maxBlockNum = local_max_block_numbers().get(backupID, -1)
    maxBlockNum = GetKnownMaxBlockNum(backupID)
    if not local_files().has_key(backupID):
        return 0, 0, 0, maxBlockNum, [(0, 0)] * suppliers_set().supplierCount
    percentPerSupplier = 100.0 / suppliers_set().supplierCount
    totalNumberOfFiles = 0
    fileNumbers = [0] * suppliers_set().supplierCount
    for blockNum in range(maxBlockNum + 1):
        if blockNum not in local_files()[backupID].keys():
            continue
#    for blockNum in local_files()[backupID].keys():
        for supplierNum in range(len(fileNumbers)):
            if supplierNum < suppliers_set().supplierCount:
                if local_files()[backupID][blockNum]['D'][supplierNum] == 1:
                    fileNumbers[supplierNum] += 1
                    totalNumberOfFiles += 1
                if local_files()[backupID][blockNum]['P'][supplierNum] == 1:
                    fileNumbers[supplierNum] += 1
                    totalNumberOfFiles += 1
    statsArray = []
    for supplierNum in range(suppliers_set().supplierCount):
        if maxBlockNum > -1:
            # 0.5 because we count both Parity and Data.
            percent = percentPerSupplier * 0.5 * fileNumbers[supplierNum] / ( maxBlockNum + 1 )
        else:
            percent = 0.0
        statsArray.append(( percent, fileNumbers[supplierNum] ))
    del fileNumbers 
    totalPercent = 100.0 * 0.5 * totalNumberOfFiles / ((maxBlockNum + 1) * suppliers_set().supplierCount)
    return totalPercent, totalNumberOfFiles, local_backup_size().get(backupID, 0), maxBlockNum, statsArray


def GetBackupBlocksAndPercent(backupID):
    if not remote_files().has_key(backupID):
        return 0, 0
    # get max block number
    # ??? maxBlockNum = remote_max_block_numbers().get(backupID, -1)
    maxBlockNum = GetKnownMaxBlockNum(backupID)
    if maxBlockNum == -1:
        return 0, 0
    # we count all remote files for this backup
    fileCounter = 0
    for blockNum in remote_files()[backupID].keys():
        for supplierNum in range(suppliers_set().supplierCount):
            if remote_files()[backupID][blockNum]['D'][supplierNum] == 1:
                fileCounter += 1
            if remote_files()[backupID][blockNum]['P'][supplierNum] == 1:
                fileCounter += 1
    # +1 since zero based and *0.5 because Data and Parity
    return maxBlockNum + 1, 100.0 * 0.5 * fileCounter / ((maxBlockNum + 1) * suppliers_set().supplierCount)

# return : blocks, percent, weak block, weak percent
def GetBackupRemoteStats(backupID, only_available_files=True):
    if not remote_files().has_key(backupID):
        return 0, 0, 0, 0
    # get max block number
    # ??? maxBlockNum = remote_max_block_numbers().get(backupID, -1)
    maxBlockNum = GetKnownMaxBlockNum(backupID)
    if maxBlockNum == -1:
        return 0, 0, 0, 0
    supplierCount = suppliers_set().supplierCount
    fileCounter = 0
    weakBlockNum = -1
    lessSuppliers = supplierCount
    activeArray = suppliers_set().GetActiveArray()
    # we count all remote files for this backup - scan all blocks
    for blockNum in range(maxBlockNum+1):
        if blockNum not in remote_files()[backupID].keys():
            lessSuppliers = 0
            weakBlockNum = blockNum
            continue
        goodSuppliers = supplierCount
        for supplierNum in range(supplierCount):
            if activeArray[supplierNum] != 1 and only_available_files:
                goodSuppliers -= 1
                continue
            if remote_files()[backupID][blockNum]['D'][supplierNum] != 1 or remote_files()[backupID][blockNum]['P'][supplierNum] != 1:
                goodSuppliers -= 1
            if remote_files()[backupID][blockNum]['D'][supplierNum] == 1:
                fileCounter += 1
            if remote_files()[backupID][blockNum]['P'][supplierNum] == 1:
                fileCounter += 1
        if goodSuppliers < lessSuppliers:
            lessSuppliers = goodSuppliers
            weakBlockNum = blockNum
    # +1 since zero based and *0.5 because Data and Parity
    return (maxBlockNum + 1, 100.0 * 0.5 * fileCounter / ((maxBlockNum + 1) * supplierCount),
            weakBlockNum, 100.0 * float(lessSuppliers) / float(supplierCount))


def GetBackupIds():
    return misc.sorted_backup_ids(remote_files().keys())


def GetKnownMaxBlockNum(backupID):
    return max(remote_max_block_numbers().get(backupID, -1), 
               local_max_block_numbers().get(backupID, -1))


def GetLocalDataArray(backupID, blockNum):
    if not local_files().has_key(backupID):
        return [0] * suppliers_set().supplierCount
    if not local_files()[backupID].has_key(blockNum):
        return [0] * suppliers_set().supplierCount
    return local_files()[backupID][blockNum]['D']


def GetLocalParityArray(backupID, blockNum):
    if not local_files().has_key(backupID):
        return [0] * suppliers_set().supplierCount
    if not local_files()[backupID].has_key(blockNum):
        return [0] * suppliers_set().supplierCount
    return local_files()[backupID][blockNum]['P']
    

def GetRemoteDataArray(backupID, blockNum):
    if not remote_files().has_key(backupID):
        return [0] * suppliers_set().supplierCount
    if not remote_files()[backupID].has_key(blockNum):
        return [0] * suppliers_set().supplierCount
    return remote_files()[backupID][blockNum]['D']

    
def GetRemoteParityArray(backupID, blockNum):
    if not remote_files().has_key(backupID):
        return [0] * suppliers_set().supplierCount
    if not remote_files()[backupID].has_key(blockNum):
        return [0] * suppliers_set().supplierCount
    return remote_files()[backupID][blockNum]['P']


def GetSupplierStats(supplierNum):
    result = {}
    files = total = 0
    for backupID in remote_files().keys():
        result[backupID] = [0, 0]
        for blockNum in remote_files()[backupID].keys():
            if remote_files()[backupID][blockNum]['D'][supplierNum] == 1:
                result[backupID][0] += 1
                files += 1 
            if remote_files()[backupID][blockNum]['P'][supplierNum] == 1:
                result[backupID][0] += 1
                files += 1
            result[backupID][1] += 2
            total += 2
    return files, total, result

def GetFailedSuppliers():
    return list(suppliers_set().failedSuppliers)

def GetSuppliersFails():
    # we try to send to this guys and we sure they are online
    # but somehow our packets was not sent correctly
    # so we remember people who have failed packets - failed suppliers
    result = {}
    for supplierNum in range(suppliers_set().supplierCount):
        idurl = suppliers_set().suppliers[supplierNum]
        result[idurl] = suppliers_set().failedPackets[supplierNum]
    dhnio.Dprint(6, 'backups.GetSuppliersFails ' + str(result))
    return result


def GetWeakLocalBlock(backupID):
    # scan all local blocks for this backup 
    # and find the worst block 
    supplierCount = suppliers_set().supplierCount
    if not local_files().has_key(backupID):
        return -1, 0, supplierCount
    maxBlockNum = GetKnownMaxBlockNum(backupID)
    weakBlockNum = -1
    lessSuppliers = supplierCount
    for blockNum in range(maxBlockNum+1):
        if blockNum not in local_files()[backupID].keys():
            return blockNum, 0, supplierCount
        goodSuppliers = supplierCount
        for supplierNum in range(supplierCount):
            if  local_files()[backupID][blockNum]['D'][supplierNum] != 1 or local_files()[backupID][blockNum]['P'][supplierNum] != 1:
                goodSuppliers -= 1
        if goodSuppliers < lessSuppliers:
            lessSuppliers = goodSuppliers
            weakBlockNum = blockNum
    return weakBlockNum, lessSuppliers, supplierCount
 
    
def GetWeakRemoteBlock(backupID):
    # scan all remote blocks for this backup 
    # and find the worst block - less suppliers keeps the data and stay online 
    supplierCount = suppliers_set().supplierCount
    if not remote_files().has_key(backupID):
        return -1, 0, supplierCount
    maxBlockNum = GetKnownMaxBlockNum(backupID)
    weakBlockNum = -1
    lessSuppliers = supplierCount
    activeArray = suppliers_set().GetActiveArray()
    for blockNum in range(maxBlockNum+1):
        if blockNum not in remote_files()[backupID].keys():
            return blockNum, 0, supplierCount
        goodSuppliers = supplierCount
        for supplierNum in range(supplierCount):
            if activeArray[supplierNum] != 1:
                goodSuppliers -= 1
                continue
            if  remote_files()[backupID][blockNum]['D'][supplierNum] != 1 or remote_files()[backupID][blockNum]['P'][supplierNum] != 1:
                goodSuppliers -= 1
        if goodSuppliers < lessSuppliers:
            lessSuppliers = goodSuppliers
            weakBlockNum = blockNum
    return weakBlockNum, lessSuppliers, supplierCount

#------------------------------------------------------------------------------ 

def SetBackupStatusNotifyCallback(callBack):
    global _BackupStatusNotifyCallback
    _BackupStatusNotifyCallback = callBack

def SetLocalFilesNotifyCallback(callback):
    global _LocalFilesNotifyCallback
    _LocalFilesNotifyCallback = callback

#def SetStatusCallBackForGuiBackup(callBack):
#    global _StatusCallBackForGuiBackup
#    StatusCallBackForGuiBackup = callBack

#------------------------------------------------------------------------------ 


if __name__ == "__main__":
    init()
    import pprint
    pprint.pprint(GetBackupIds())











