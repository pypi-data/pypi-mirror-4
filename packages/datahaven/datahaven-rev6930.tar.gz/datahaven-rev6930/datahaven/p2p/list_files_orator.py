#!/usr/bin/env python
#list_files_orator.py
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2012
#    Use of this software constitutes acceptance of the Terms of Use
#      http://datahaven.net/terms_of_use.html
#    All rights reserved.
#
#

import os
import sys

try:
    from twisted.internet import reactor
except:
    sys.exit('Error initializing twisted.internet.reactor in list_files_orator.py')
from twisted.internet.defer import maybeDeferred
from twisted.internet.task import LoopingCall


from lib.automat import Automat
import lib.dhnio as dhnio
import lib.contacts as contacts


import backup_monitor
import p2p_connector
import lib.automats as automats

import backups 
import customerservice
import contacts_status


_ListFilesOrator = None
_RequestedListFilesPacketIDs = set()
_RequestedListFilesCounter = 0

#------------------------------------------------------------------------------

def A(event=None, arg=None):
    global _ListFilesOrator
    if _ListFilesOrator is None:
        _ListFilesOrator = ListFilesOrator('list_files_orator', 'NO_FILES', 4)
    if event is not None:
        _ListFilesOrator.automat(event, arg)
    return _ListFilesOrator


class ListFilesOrator(Automat):
    timers = {'timer-1min':  (60, ['REMOTE_FILES']), }

    def state_changed(self, oldstate, newstate):
        #automats.set_global_state('ORATOR ' + newstate)
        backup_monitor.A('list_files_orator.state', newstate)

    def A(self, event, arg):
        #---NO_FILES---
        if self.state == 'NO_FILES':
            if event == 'need-files':
                self.doReadLocalFiles()
                self.state = 'LOCAL_FILES'
        #---LOCAL_FILES---
        elif self.state == 'LOCAL_FILES':
            if event == 'local-files-done' and p2p_connector.A().state is 'CONNECTED':
                
                self.doRequestRemoteFiles()
                self.state = 'REMOTE_FILES'
            elif event == 'local-files-done' and p2p_connector.A().state is not 'CONNECTED':
                self.state = 'NO_FILES'
        #---REMOTE_FILES---
        elif self.state == 'REMOTE_FILES':
            if ( event == 'timer-1min' and self.isSomeListFilesReceived() ) or ( event == 'inbox-files' and self.isAllListFilesReceived() ):
                self.state = 'SAW_FILES'
            elif event == 'timer-1min' and not self.isSomeListFilesReceived():
                self.state = 'NO_FILES'
        #---SAW_FILES---
        elif self.state == 'SAW_FILES':
            if event == 'need-files':
                self.doReadLocalFiles()
                self.state = 'LOCAL_FILES'

    def isAllListFilesReceived(self):
        global _RequestedListFilesPacketIDs
        dhnio.Dprint(6, 'list_files_orator.isAllListFilesReceived need %d more' % len(_RequestedListFilesPacketIDs))
        return len(_RequestedListFilesPacketIDs) == 0

    def isSomeListFilesReceived(self):
        global _RequestedListFilesCounter
        dhnio.Dprint(6, 'list_files_orator.isSomeListFilesReceived %d list files was received' % _RequestedListFilesCounter)
        return _RequestedListFilesCounter > 0

    def doReadLocalFiles(self):
        maybeDeferred(backups.ReadLocalFiles).addBoth(
            lambda x: self.automat('local-files-done'))
    
    def doRequestRemoteFiles(self):
        global _RequestedListFilesCounter
        global _RequestedListFilesPacketIDs
        _RequestedListFilesCounter = 0
        _RequestedListFilesPacketIDs.clear()
        for idurl in contacts.getSupplierIDs():
            if contacts_status.isOnline(idurl):
                customerservice.RequestListFiles(idurl)
                _RequestedListFilesPacketIDs.add(idurl)
                
#    def doReadSavedRemoteListFiles(self):
#        backups.ReadLatestRawListFiles()
    

def IncommingListFiles(supplierNum, packet, listFileText):
    global _RequestedListFilesPacketIDs
    global _RequestedListFilesCounter
    _RequestedListFilesCounter += 1
    _RequestedListFilesPacketIDs.discard(packet.OwnerID)
    A('inbox-files', (supplierNum, packet, listFileText))
    
    


