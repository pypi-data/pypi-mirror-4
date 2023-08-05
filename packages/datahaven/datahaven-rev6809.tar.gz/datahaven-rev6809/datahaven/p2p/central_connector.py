#!/usr/bin/env python
#central_connector.py
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2012
#    All rights reserved.
#
#

import os
import sys

try:
    from twisted.internet import reactor
except:
    sys.exit('Error initializing twisted.internet.reactor in central_connector.py')
from twisted.internet.defer import Deferred, maybeDeferred
from twisted.internet.task import LoopingCall


import lib.dhnio as dhnio
import lib.misc as misc
import lib.packetid as packetid
import lib.settings as settings
import lib.contacts as contacts
import lib.transport_control as transport_control
from lib.automat import Automat


import lib.automats as automats
import p2p_connector
import central_service
import money

import identitypropagate


_CentralConnector = None

#------------------------------------------------------------------------------ 

def A(event=None, arg=None):
    global _CentralConnector
    if _CentralConnector is None:
        _CentralConnector = CentralConnector('central_connector', 'AT_STARTUP', 4)
    if event is not None:
        _CentralConnector.automat(event, arg)
    return _CentralConnector

class CentralConnector(Automat):
    timers = {'timer-1hour':  (60*60, ['CONNECTED', 'DISCONNECTED', 'ONLY_ID']),
              'timer-30sec':  (30,    ['IDENTITY', 'REQUEST_SETTINGS', 'SETTINGS', 'SUPPLIERS',]),
              'timer-10sec':  (10,    ['IDENTITY'])}
    flagSettings = False

    def state_changed(self, oldstate, newstate):
        automats.set_global_state('CENTRAL ' + newstate)
        p2p_connector.A('central_connector.state', newstate)

    def A(self, event, arg):
        #---AT_STARTUP---
        if self.state == 'AT_STARTUP':
            if event == 'propagate':
                self.flagSettings = False
                self.doInitCentralService()
                self.doSendIdentity()
                self.state = 'IDENTITY'
        #---IDENTITY---
        elif self.state == 'IDENTITY':
            if event == 'identity-ack' and not self.isSettingsExist():
                self.doSendRequestSettings()
                self.state = 'REQUEST_SETTINGS'
            elif event == 'identity-ack' and self.isSettingsExist() and not self.flagSettings:
                self.doSendSettings()
                self.state = 'SETTINGS'
            elif event == 'identity-ack' and self.isSettingsExist() and self.flagSettings and not self.isSuppliersNeeded():
                self.doSendBandWidthReport()
                self.state = 'CONNECTED'
            elif event == 'identity-ack' and self.isSettingsExist() and self.flagSettings and self.isSuppliersNeeded():
                self.doSendRequestSuppliers()
                self.state = 'SUPPLIERS'
            elif event == 'timer-10sec':
                self.doSendIdentity()
            elif event == 'timer-30sec':
                self.state = 'DISCONNECTED'
        #---SETTINGS---
        elif self.state == 'SETTINGS':
            if event == 'settings-ack':
                self.flagSettings = True
                self.state = 'SUPPLIERS'
            elif event == 'list-suppliers':
                self.flagSettings = True
                self.doSendBandWidthReport()
                self.state = 'CONNECTED'
            elif event == 'propagate':
                self.doSendIdentity()
                self.state = 'IDENTITY'
            elif event == 'timer-30sec':
                self.state = 'ONLY_ID'
            elif event == 'settings':
                self.doSendSettings()
        #---REQUEST_SETTINGS---
        elif self.state == 'REQUEST_SETTINGS':
            if event == 'request-settings-ack' and self.isSuppliersNeeded():
                self.flagSettings = True
                self.state = 'SUPPLIERS'
            elif event == 'request-settings-ack' and not self.isSuppliersNeeded():
                self.flagSettings = True
                self.doSendBandWidthReport()
                self.state = 'CONNECTED'
            elif event == 'propagate':
                self.doSendIdentity()
                self.state = 'IDENTITY'
            elif event == 'timer-30sec':
                self.state = 'ONLY_ID'
        #---SUPPLIERS---
        elif self.state == 'SUPPLIERS':
            if event == 'list-suppliers':
                self.doSendBandWidthReport()
                self.state = 'CONNECTED'
            elif event == 'propagate':
                self.doSendIdentity()
                self.state = 'IDENTITY'
            elif event == 'timer-30sec':
                self.state = 'ONLY_ID'
        #---ONLY_ID---
        elif self.state == 'ONLY_ID':
            if event in ['timer-1hour', 'propagate', 'settings', 'identity-ack', 'list-suppliers', 'list-customers']:
                self.doSendIdentity()
                self.state = 'IDENTITY'
        #---CONNECTED---
        elif self.state == 'CONNECTED':
            if event in ['propagate', 'timer-1hour']:
                self.doSendIdentity()
                self.state = 'IDENTITY'
            elif event == 'settings':
                self.doSendSettings()
                self.flagSettings = False
                self.state = 'SETTINGS'
        #---DISCONNECTED---
        elif self.state == 'DISCONNECTED':
            if ( event in ['timer-1hour', 'propagate', 'settings', 'identity-ack', 'list-suppliers', 'list-customers'] ) or ( event == 'p2p_connector.state' and arg is 'CONNECTED' ):
                self.flagSettings = False
                self.doSendIdentity()
                self.state = 'IDENTITY'

    def isSettingsExist(self):
        return settings.getCentralNumSuppliers() > 0

    def isSuppliersNeeded(self):
        return settings.getCentralNumSuppliers() <= 0 or \
               contacts.numSuppliers() != settings.getCentralNumSuppliers()

    def _saveRequestedSettings(self, newpacket):
        sd = dhnio._unpack_dict(newpacket.Payload)
        settings.uconfig().set('central-settings.needed-megabytes', sd.get('n', str(settings.DefaultNeededMb())+'Mb'))
        settings.uconfig().set('central-settings.shared-megabytes', sd.get('d', str(settings.DefaultDonatedMb())+'Mb'))
        settings.uconfig().set('central-settings.desired-suppliers', sd.get('s', '2'))
        settings.uconfig().set('emergency.emergency-email', sd.get('e1', ''))
        settings.uconfig().set('emergency.emergency-phone', sd.get('e2', ''))
        settings.uconfig().set('emergency.emergency-fax', sd.get('e3', ''))
        settings.uconfig().set('emergency.emergency-text', sd.get('e4', '').replace('<br>', '\n'))
        settings.uconfig().update()
        reactor.callLater(0, self.automat, 'request-settings-ack', newpacket)

    def doInitCentralService(self):
        central_service.init()

    def doSendIdentity(self):
        transport_control.RegisterInterest(
            lambda packet: self.automat('identity-ack', packet),
            settings.CentralID(),
            central_service.SendIdentity(True))

    def doSendSettings(self):
        packetID = packetid.UniqueID()
        transport_control.RegisterInterest(
            self.settingsAck,
            settings.CentralID(),
            packetID)
        central_service.SendSettings(True, packetID)

    def doSendRequestSettings(self):
        transport_control.RegisterInterest(
            lambda packet: self._saveRequestedSettings(packet),
            settings.CentralID(),
            central_service.SendRequestSettings(True))

    def doSendRequestSuppliers(self):
        return central_service.SendRequestSuppliers()

    def settingsAck(self, packet):
        try:
            status, last_receipt, = packet.Payload.split('\n', 2)
            last_receipt = int(last_receipt)
        except:
            status = 'error'
            last_receipt = -1
        dhnio.Dprint(4, 'central_connector.settingsAck [%s] last_receipt=%d' % (status, last_receipt))
        missing_receipts = money.SearchMissingReceipts(last_receipt)
        if len(missing_receipts) > 0:
            reactor.callLater(0, central_service.SendRequestReceipt, missing_receipts)
        self.automat('settings-ack', packet)

    def doSendBandWidthReport(self):
        central_service.LoopSendBandwidthReport()
        
        
