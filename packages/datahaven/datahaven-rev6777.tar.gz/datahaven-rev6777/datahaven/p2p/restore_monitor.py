#!/usr/bin/python
#restore_monitor.py
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2012
#    All rights reserved.
#
#
#manage currently restoring backups

import os
import sys
import time


import lib.dhnio as dhnio


import restore


_WorkingBackupIDs = {}
_WorkingRestoreProgress = {}
OnRestorePacketFunc = None
OnRestoreDoneFunc = None

#------------------------------------------------------------------------------ 

def init():
    dhnio.Dprint(4, 'restore_monitor.init')

def packet_in_callback(backupID, packet):
    dhnio.Dprint(4, 'restore_monitor.packet_in_callback ' + backupID)
    global _WorkingRestoreProgress
    global OnRestorePacketFunc
    
    SupplierNumber = packet.SupplierNumber()
    
    #want to count the data we restoring
    if SupplierNumber not in _WorkingRestoreProgress[backupID].keys():
        _WorkingRestoreProgress[backupID][SupplierNumber] = 0
    _WorkingRestoreProgress[backupID][SupplierNumber] += len(packet.Payload)

    if OnRestorePacketFunc is not None:
        OnRestorePacketFunc(backupID, SupplierNumber, packet)

def restore_done(x):
    dhnio.Dprint(2, 'restore_monitor.restore_done ' + str(x))
    global _WorkingBackupIDs
    global _WorkingRestoreProgress
    global OnRestoreDoneFunc
    
    backupID = x.split(' ')[0]
    _WorkingBackupIDs.pop(backupID, None)
    _WorkingRestoreProgress.pop(backupID, None)
    
    if OnRestoreDoneFunc is not None:
        OnRestoreDoneFunc(backupID, 'done')

def restore_failed(x, why='failed'):
    dhnio.Dprint(2, 'restore_monitor.restore_failed ' + str(x))
    global _WorkingBackupIDs
    global _WorkingRestoreProgress
    global OnRestoreDoneFunc

    backupID = x.split(' ')[0]
    _WorkingBackupIDs.pop(backupID, None)
    _WorkingRestoreProgress.pop(backupID, None)

    if OnRestoreDoneFunc is not None:
        OnRestoreDoneFunc(backupID, why)

def Start(backupID, outputFileName):
    dhnio.Dprint(6, 'restore_monitor.Start %s to %s' % (backupID, outputFileName))
    global _WorkingBackupIDs
    global _WorkingRestoreProgress
    if backupID in _WorkingBackupIDs.keys():
        return None
    try:
        outputFile = open(outputFileName, "wb")
    except:
        dhnio.Dprint(2, 'restore_monitor.Start ERROR can not open output file %s' % outputFileName)
        restore_failed(backupID, 'file_open_error')
        return None
       
    r = restore.restore(backupID, outputFile)
    r.MyDeferred.addCallback(restore_done)
    r.MyDeferred.addErrback(restore_failed)
    r.SetPacketInCallback(packet_in_callback)
    _WorkingBackupIDs[backupID] = r
    _WorkingRestoreProgress[backupID] = {}
    return r

def Abort(backupID):
    dhnio.Dprint(6, 'restore_monitor.Abort %s' % backupID)
    global _WorkingBackupIDs
    global _WorkingRestoreProgress
    if not backupID in _WorkingBackupIDs.keys():
        return False
    r = _WorkingBackupIDs[backupID]
    r.Abort()
    return True

def GetWorkingIDs():
    global _WorkingBackupIDs
    return _WorkingBackupIDs.keys()

def IsWorking(backupID):
    global _WorkingBackupIDs
    return backupID in _WorkingBackupIDs.keys()

def GetProgress(backupID):
    global _WorkingRestoreProgress
    return _WorkingRestoreProgress.get(backupID, {})







