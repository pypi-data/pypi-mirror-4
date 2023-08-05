#!/usr/bin/python
#backup_db_keeper.py
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2012
#    Use of this software constitutes acceptance of the Terms of Use
#      http://datahaven.net/terms_of_use.html
#    All rights reserved.
#

import os
import sys

#------------------------------------------------------------------------------ 

try:
    from twisted.internet import reactor
except:
    sys.exit('Error initializing twisted.internet.reactor in backup_rebuilder.py')
    
import lib.dhnio as dhnio
import lib.misc as misc
import lib.contacts as contacts
import lib.settings as settings
import lib.transport_control as transport_control
import lib.dhnpacket as dhnpacket
import lib.commands as commands
import lib.automats as automats
from lib.automat import Automat

import p2p_connector
import io_throttle


_BackupDBKeeper = None
   
#------------------------------------------------------------------------------ 

def A(event=None, arg=None):
    global _BackupDBKeeper
    if _BackupDBKeeper is None:
        _BackupDBKeeper = BackupDBKeeper('backup_db_keeper', 'AT_STARTUP', 4)
    if event is not None:
        _BackupDBKeeper.automat(event, arg)
    return _BackupDBKeeper
    
#------------------------------------------------------------------------------ 

class BackupDBKeeper(Automat):
    timers = {'timer-1sec':     (1,     ['RESTART']),
              'timer-30sec':    (30,    ['RESTART', 'REQUEST', 'SENDING']),
              'timer-1hour':    (60*60, ['READY']),}
    
    def init(self):
        self.requestedSuppliers = set()
        self.sentSuppliers = set()

    def A(self, event, arg):
        #---AT_STARTUP---
        if self.state == 'AT_STARTUP':
            if event == 'restart':
                self.state = 'RESTART'
            elif event == 'init':
                self.state = 'READY'
        #---RESTART---
        elif self.state == 'RESTART':
            if event == 'timer-1sec' and p2p_connector.A().state is 'CONNECTED':
                self.doSuppliersRequestDBInfo(arg)
                self.state = 'REQUEST'
            elif event == 'timer-30sec':
                self.state = 'READY'
        #---REQUEST---
        elif self.state == 'REQUEST':
            if event == 'restart':
                self.state = 'RESTART'
            elif ( event == 'incomming-db-info' and self.isAllSuppliersResponded(arg) ) or event == 'timer-30sec':
                self.doSuppliersSendDBInfo(arg) 
                self.state = 'SENDING'
        #---SENDING---
        elif self.state == 'SENDING':
            if event == 'restart':
                self.state = 'RESTART'
            elif ( event == 'db-info-acked' and self.isAllSuppliersAcked(arg) ) or event == 'timer-30sec':
                self.state = 'READY'
        #---READY---
        elif self.state == 'READY':
            if event in ['timer-1hour', 'restart']:
                self.state = 'RESTART'
            
    def isAllSuppliersResponded(self, arg):
        return len(self.requestedSuppliers) == 0
            
    def isAllSuppliersAcked(self, arg):
        return len(self.sentSuppliers) == 0
            
    def doSuppliersRequestDBInfo(self, arg):
        Payload = ''
        localID = misc.getLocalID()
        packetID = settings.BackupInfoFileName()
        for supplierId in contacts.getSupplierIDs():
            newpacket = dhnpacket.dhnpacket(commands.Retrieve(), localID, localID, packetID, Payload, supplierId)
            transport_control.outboxAck(newpacket)
            transport_control.RegisterInterest(self.SupplierResponse, supplierId, packetID)
#            io_throttle.QueueRequestFile(
#                self.SupplierResponse, 
#                misc.getLocalID(), 
#                settings.BackupInfoFileName(), 
#                misc.getLocalID(), 
#                supidurl)
            self.requestedSuppliers.add(supplierId)
            dhnio.Dprint(6, 'backup_db_keeper.doSuppliersRequestDBInfo to %s' % supplierId)

    def doSuppliersSendDBInfo(self, arg):
        if os.path.isfile(settings.BackupInfoFileFullPathOld()):
            # TODO - let's remove this in future
            # I just want to rename backup_info.xml to backup_db
            try:
                os.rename(settings.BackupInfoFileFullPathOld(), settings.BackupInfoFileFullPath())
            except:
                dhnio.DprintException()
        Payload = dhnio.ReadBinaryFile(settings.BackupInfoFileFullPath())
        localID = misc.getLocalID()
        packetID = settings.BackupInfoFileName()
        for supplierId in contacts.getSupplierIDs():
            newpacket = dhnpacket.dhnpacket(commands.Data(), localID, localID, packetID, Payload, supplierId)
            transport_control.outboxAck(newpacket)
            transport_control.RegisterInterest(self.SupplierAcked, supplierId, packetID)
#            io_throttle.QueueSendFile(
#                settings.BackupInfoFileFullPath(),
#                settings.BackupInfoFileName(),
#                supidurl,
#                misc.getLocalID(), 
#                self.SupplierAcked,
#                self.SupplierFailed)
            self.sentSuppliers.add(supplierId)
            dhnio.Dprint(6, 'backup_db_keeper.doSuppliersSendDBInfo to %s' % supplierId)

    def SupplierResponse(self, packet):
        self.requestedSuppliers.discard(packet.RemoteID)
        dhnio.Dprint(6, 'backup_db_keeper.SupplierResponse %s, %d more suppliers' % (packet.RemoteID, len(self.requestedSuppliers)))

    def SupplierAcked(self, packet):
        self.sentSuppliers.discard(packet.RemoteID)
        dhnio.Dprint(6, 'backup_db_keeper.SupplierAcked %s, %d more suppliers' % (packet.RemoteID, len(self.sentSuppliers)))
        self.automat('db-info-acked', packet.RemoteID)
    
    def SupplierFailed(self, remoteID, packetID, why):
        self.sentSuppliers.discard(remoteID)
        dhnio.Dprint(6, 'backup_db_keeper.SupplierFailed %s, %d more suppliers' % (remoteID, len(self.sentSuppliers)))
        self.automat('db-info-acked', remoteID)


