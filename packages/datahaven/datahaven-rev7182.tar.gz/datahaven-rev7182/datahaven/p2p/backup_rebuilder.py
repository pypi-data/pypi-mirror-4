#!/usr/bin/python
#backup_rebuilder.py
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
    sys.exit('Error initializing twisted.internet.reactor in backup_rebuilder.py')

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
import backup_monitor
import block_rebuilder
import lib.automats as automats

import backups
import raidread
import io_throttle
import backup_db

_BackupRebuilder = None
_StoppedFlag = True
_BackupIDsQueue = []  
_BlockRebuildersQueue = []

#------------------------------------------------------------------------------ 

def A(event=None, arg=None):
    global _BackupRebuilder
    if _BackupRebuilder is None:
        _BackupRebuilder = BackupRebuilder('backup_rebuilder', 'STOPPED', 8)
    if event is not None:
        _BackupRebuilder.automat(event, arg)
    return _BackupRebuilder


class BackupRebuilder(Automat):
    timers = {'timer-1sec':     (1,     ['NEXT_BACKUP']),
              'timer-01sec':    (0.1,   ['NEXT_BLOCK']), }
    
    def init(self):
        self.currentBackupID = None             # currently working on this backup
        self.currentBlockNumber = -1            # currently working on this block
        self.workingBlocksQueue = []            # list of missing blocks we work on for current backup 
        self.maxBlockRebuilderQueueLength = 8   # TODO - need to sort out what is an appropriate length

    def state_changed(self, oldstate, newstate):
        automats.set_global_state('REBUILD ' + newstate)
        backup_monitor.A('backup_rebuilder.state', newstate)
        
    def A(self, event, arg):
        #---STOPPED---
        if self.state is 'STOPPED':
            if event == 'start' :
                self.doClearStoppedFlag(arg)
                self.state = 'NEXT_BACKUP'
            elif event == 'init' :
                pass
        #---NEXT_BACKUP---
        elif self.state is 'NEXT_BACKUP':
            if event == 'timer-1sec' and not self.isStopped(arg) and self.isMoreBackups(arg) :
                self.doTakeNextBackup(arg)
                self.doTakeNextBlock(arg)
                self.state = 'NEXT_BLOCK'
            elif event == 'timer-1sec' and not self.isMoreBackups(arg) and not self.isStopped(arg) :
                self.state = 'DONE'
            elif event == 'timer-1sec' and self.isStopped(arg) :
                self.state = 'STOPPED'
        #---NEXT_BLOCK---
        elif self.state is 'NEXT_BLOCK':
            if event == 'timer-01sec' and not self.isStopped(arg) and self.isMoreBlocks(arg) and not self.isFailedSuppliers(arg) and self.isSpaceForNewBlockRebuilder(arg) :
                self.doStartNewBlockRebuilder(arg)
                self.state = 'REBUILDING'
            elif event == 'timer-01sec' and not self.isStopped(arg) and not self.isMoreBlocks(arg) and self.isMoreBackups(arg) :
                self.state = 'NEXT_BACKUP'
            elif event == 'timer-01sec' and ( ( not self.isMoreBackups(arg) and not self.isMoreBlocks(arg) ) or self.isFailedSuppliers(arg) ) :
                self.state = 'DONE'
            elif event == 'timer-1sec' and self.isStopped(arg) :
                self.state = 'STOPPED'
        #---REBUILDING---
        elif self.state is 'REBUILDING':
            if ( event == 'block_rebuilder.state' and arg in [ 'FINISHED' , 'STOPPED' , 'DONE' ] ) :
                self.doTakeNextBlock(arg)
                self.state = 'NEXT_BLOCK'
            elif ( event == 'block_rebuilder.state' and arg is 'TIMEOUT' ) :
                self.state = 'DONE'
        #---DONE---
        elif self.state is 'DONE':
            if event == 'start' :
                self.doClearStoppedFlag(arg)
                self.state = 'NEXT_BACKUP'

    def isStopped(self, arg):
        return ReadStoppedFlag() == True # :-)

    def isMoreBackups(self, arg):
        global _BackupIDsQueue
        return len(_BackupIDsQueue) > 0
    
    def isMoreBlocks(self, arg):
        # because started from 0,  -1 means not found 
        return self.currentBlockNumber > -1 
    
    def isSpaceForNewBlockRebuilder(self, arg):
        global _BlockRebuildersQueue
        return len(_BlockRebuildersQueue) < self.maxBlockRebuilderQueueLength

    def isFailedSuppliers(self, arg):
        failed_suppliers = backups.GetFailedSuppliers()
        dhnio.Dprint(6, 'backup_rebuilder.isFailedSuppliers return %s: %s' % (str(len(failed_suppliers) > 0), failed_suppliers))
        return len(failed_suppliers) > 0

    def doTakeNextBackup(self, arg):
        global _BackupIDsQueue
        # take a first backup from queue to work on it
        backupID = _BackupIDsQueue.pop(0)
        # dhnio.Dprint(6, 'backup_rebuilder.doTakeNextBackup first backup in queue is %s' % backupID)
        # if remote data structure is not exist for this backup - create it
        # this mean this is only local backup!
        if not backups.remote_files().has_key(backupID):
            backups.remote_files()[backupID] = {}
            # we create empty remote info for every local block
            # range(0) should return []
            for blockNum in range(backups.local_max_block_numbers().get(backupID, -1) + 1):
                backups.remote_files()[backupID][blockNum] = {
                    'D': [0] * backups.suppliers_set().supplierCount,
                    'P': [0] * backups.suppliers_set().supplierCount }
        # clear blocks queue from previous iteration
        self.currentBlockNumber = -1
        # del self.workingBlocksQueue
        self.workingBlocksQueue = [] 
        # detect missing blocks from remote info
        self.workingBlocksQueue = backups.ScanMissingBlocks(backupID)
        # find the correct max block number for this backup
        # we can have remote and local files
        # will take biggest block number from both 
        backupMaxBlock = max(backups.remote_max_block_numbers().get(backupID, -1),
                             backups.local_max_block_numbers().get(backupID, -1))
        # now need to remember this biggest block number
        # remote info may have less blocks - need to create empty info for missing blocks
        for blockNum in range(backupMaxBlock + 1):
            if backups.remote_files()[backupID].has_key(blockNum):
                continue
            backups.remote_files()[backupID][blockNum] = {
                'D': [0] * backups.suppliers_set().supplierCount,
                'P': [0] * backups.suppliers_set().supplierCount }
        # really take next backup
        self.currentBackupID = backupID
        # clear sending queue, remove old packets for this backup, we will send them again
        io_throttle.DeleteBackupRequests(self.currentBackupID)
        # dhnio.Dprint(6, 'backup_rebuilder.doTakeNextBackup currentBackupID=%s workingBlocksQueue=%d' % (self.currentBackupID, len(self.workingBlocksQueue)))
       
    def doTakeNextBlock(self, arg):
        if len(self.workingBlocksQueue) > 0:
            # let's take last blocks first ... 
            # in such way we can propagate how big is the whole backup as soon as possible!
            # remote machine can multiply [file size] * [block number] 
            # and calculate the whole size to be received ... smart!
            # ... remote supplier should not use last file to calculate
            self.currentBlockNumber = self.workingBlocksQueue.pop()
            # self.currentBlockNumber = self.workingBlocksQueue.pop(0)
        else:
            self.currentBlockNumber = -1

    def doStartNewBlockRebuilder(self, arg):
        br = block_rebuilder.BlockRebuilder(
            eccmap.Current(), #self.eccMap,
            self.currentBackupID,
            self.currentBlockNumber,
            backups.suppliers_set(),
            backups.GetRemoteDataArray(self.currentBackupID, self.currentBlockNumber),
            backups.GetRemoteParityArray(self.currentBackupID, self.currentBlockNumber),
            backups.GetLocalDataArray(self.currentBackupID, self.currentBlockNumber),
            backups.GetLocalParityArray(self.currentBackupID, self.currentBlockNumber),)
        AddBlockRebuilder(br)
        br.automat('start')
        dhnio.Dprint(6, 'backup_rebuilder.doStartNewBlockRebuilder for %s blockNum=%s' % ( 
            self.currentBackupID, self.currentBlockNumber))

    def doClearStoppedFlag(self, arg):
        ClearStoppedFlag()

#    def doSetStoppedFlag(self):
#        SetStoppedFlag()
        
#    def doStartRepainting(self):
#        RepaintingProcess(True)
        
#    def doStopRepainting(self):
#        RepaintingProcess(False)

#------------------------------------------------------------------------------ 

def AddBackupsToWork(backupIDs):
    global _BackupIDsQueue 
    _BackupIDsQueue.extend(backupIDs)


def RemoveBackupToWork(backupID):
    global _BackupIDsQueue
    if backupID in _BackupIDsQueue:
        _BackupIDsQueue.remove(backupID)


def SetStoppedFlag():
    global _StoppedFlag
    _StoppedFlag = True
    
    
def ClearStoppedFlag():
    global _StoppedFlag
    _StoppedFlag = False
    

def ReadStoppedFlag():
    global _StoppedFlag
    return _StoppedFlag
    
    
def AddBlockRebuilder(obj):
    global _BlockRebuildersQueue
    _BlockRebuildersQueue.append(obj)
    

def RemoveBlockRebuilder(obj):
    global _BlockRebuildersQueue
    _BlockRebuildersQueue.remove(obj)
    


    
    

    
