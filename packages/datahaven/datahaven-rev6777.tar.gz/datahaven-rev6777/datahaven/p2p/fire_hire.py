#!/usr/bin/python
#fire_hire.py
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2012
#    All rights reserved.
#
#  We contact datahaven.net for list of nodes we have hired
#   and we can also replace any node (fire & hire someone else at once)
#   by contacting datahaven.net and asking for replacement.
#
#  If at some point we are not getting good answers from a node
#  for too long we need to replace him and reconstruct the data
#  he was holding.  This is fire_hire and then scrubbing.
#
#  Probably if we try to contact someone for 48 hours and can not,
#  we want to give up on them.
#
#  GUI can fire_hire at any time.
#
#  Automatically fire if right after we ask a supplier for a BigPacket,
#    he turns around and asks us for it (like he does not have it).
#    Our regular code would not do this, but an evil modified version might
#       try to get away with not holding any data by just getting it from us
#       anytime we asked for it.  So we can not allow this cheat to work.
#
#  We ask for lists of files they have for us and keep these in  settings.FileListDir()/suppliernum
#  These should be updated at least every night.
#  If a supplier has not given us a list for several days he is a candidate for firing.
#
#  Transport_control should keep statistics on how fast different nodes are.
#  We could fire a slow node.
#
#  Restore can keep track of who did not answer in time to be part of raidread, and they can
#  be a candidate for firing.
#
#  The fire packet needs to use IDURL so that if there is a retransmission of the "fire" request
#    we just send new "list suppliers" again.
#
#  Task list
#  1) fire inactive suppliers (default is 48 hours)
#  2) fire suppliers with low rating (less than 25% by default)
#  3) test if supplier is "evil modifed"
#  4) test ListFiles peridoically
#  5) fire slow nodes



import os
import sys
import time


try:
    from twisted.internet import reactor
except:
    sys.exit('Error initializing twisted.internet.reactor in fire_hire.py')

from twisted.internet import task


import lib.dhnio as dhnio
import lib.misc as misc
import lib.settings as settings
import lib.contacts as contacts
import lib.transport_control as transport_control
import lib.nameurl as nameurl
from lib.automat import Automat


import backup_monitor
import lib.automats as automats

import backups
import central_service
import ratings
import backup_db
import events
import contacts_status
import identitypropagate


#-------------------------------------------------------------------------------

_FireHire = None
_StatusTask = None
_LogFile = None

#-------------------------------------------------------------------------------

def A(event=None, arg=None):
    global _FireHire
    if _FireHire is None:
        _FireHire = FireHire('fire_hire', 'READY', 4)
    if event is not None:
        _FireHire.automat(event, arg)
    return _FireHire

class FireHire(Automat):
    timers = {'timer-30sec': (30, ['CALL_ALL']),
              'timer-1min':  (60, ['FIRE_HIM!'])}
    
    def init(self):
        self.lastFireTime = 0

    def state_changed(self, oldstate, newstate):
        automats.set_global_state('FIREHIRE ' + newstate)

    def A(self, event, arg):
        #---READY---
        if self.state == 'READY':
            if event == 'start' and self.isTimePassed():
                self.doCallAllSuppliers()
                self.state = 'CALL_ALL'
            elif event == 'fire-him-now':
                self.doSendFirePacket(arg)
                self.state = 'FIRE_HIM!'
            elif event == 'start' and not self.isTimePassed():
                backup_monitor.A('fire-hire-finished')
        #---CALL_ALL---
        elif self.state == 'CALL_ALL':
            if event == 'timer-30sec':
                self.doFindLostSupplier()
                self.state = 'LOST_SUPPLIER'
            elif event == 'fire-him-now':
                self.doSendFirePacket(arg)
                self.state = 'FIRE_HIM!'
        #---LOST_SUPPLIER---
        elif self.state == 'LOST_SUPPLIER':
            if event == 'found-one-lost-supplier':
                self.doSendFirePacket(arg)
                self.state = 'FIRE_HIM!'
            elif event == 'not-found-lost-suppliers':
                backup_monitor.A('fire-hire-finished')
                self.state = 'READY'
        #---FIRE_HIM!---
        elif self.state == 'FIRE_HIM!':
            if event == 'timer-1min':
                backup_monitor.A('fire-hire-finished')
                self.state = 'READY'
            elif event == 'list-suppliers' and self.isNewSupplierListed(arg):
                backup_monitor.A('hire-new-supplier')
                self.state = 'READY'
                
    def isTimePassed(self):
        dhnio.Dprint(6, 'fire_hire.isTimePassed last "fire" was %d minutes ago' % ((time.time() - self.lastFireTime) / 60.0))
        return time.time() - self.lastFireTime > settings.FireHireMinimumDelay()
                
    def isNewSupplierListed(self, arg):
        # now we just check that new list of suppliers
        # is not equal with the list of current suppliers 
        return arg[0] != arg[1]
                
    def doCallAllSuppliers(self):
        self.suppliersCalled = contacts.getSupplierIDs()
        identitypropagate.suppliers(
            lambda packet: self.automat('identity-ack', packet))
    
    def doSendFirePacket(self, arg):
        if isinstance(arg, tuple):
            central_service.SendChangeSupplier(arg[0], arg[1])
        else:
            central_service.SendReplaceSupplier(arg)
        self.lastFireTime = time.time()
    
    def doFindLostSupplier(self):
        e, a = WhoIsLost()
        self.automat(e, a)
    
    def doCallNewSupplier(self, arg):
        idurl = arg[0][arg[1]]
        identitypropagate.single(idurl, 
            lambda packet: self.automat('ack-from-new-supplier', packet))
        
#------------------------------------------------------------------------------ 

def WhoIsLost():
    # we want to fire user if we try to send to him but this was failed 3 times or more, 
    # we check this first, because this is more important than other things.
    # many things can be a reason: slow connection, old code, network errors.
    # timeout during sending of our packets - this is what we trying to deal here! 
    if len(backups.GetFailedSuppliers()) > 0:
        suppliers_fails = backups.GetSuppliersFails()
        worst_supplier = ''
        most_fails = 0
        for idurl, fails in suppliers_fails.items():
            if fails > most_fails:
                worst_supplier = idurl
                most_fails = fails 
#        if most_fails >= 3:
        dhnio.Dprint(2, 'fire_hire.WhoIsLost !!!!!!!! [%s] is failed supplier - %d fails!' % (nameurl.GetName(worst_supplier), most_fails))
        return 'found-one-lost-supplier', worst_supplier
#        else:
#            dhnio.Dprint(4, 'fire_hire.WhoIsLost %s have only %d fails, not this time ... ' % (nameurl.GetName(worst_supplier), most_fails))
#            return 'not-found-lost-suppliers', ''
    # we only fire offline suppliers
    offline_suppliers = {}
    # ask backup_monitor about current situation
    # check every offline supplier and see
    # how many files he keep at the moment
    for supplierNum in range(contacts.numSuppliers()):
        idurl = contacts.getSupplierID(supplierNum)
        if not contacts_status.isOnline(idurl):
            blocks, total, stats = backups.GetSupplierStats(supplierNum)
            rating = 0 if total == 0 else blocks / total 
            offline_suppliers[idurl] = rating
    # if all suppliers are online - we are very happy - no need to fire anybody ! 
    if len(offline_suppliers) == 0:
        dhnio.Dprint(4, 'fire_hire.WhoIsLost no offline suppliers, Cool!')
        # self.automat('not-found-lost-suppliers')
        return 'not-found-lost-suppliers', ''
    # sort users - we always fire worst supplier 
    rating = offline_suppliers.keys()
    rating.sort(key=lambda idurl: offline_suppliers[idurl])
    lost_supplier_idurl = rating[0]
    # we do not want to fire this man if he store at least 50% of our files
    # the fact that he is offline is not enough to fire hime !
    if offline_suppliers[lost_supplier_idurl] < 0.5:
        dhnio.Dprint(4, 'fire_hire.WhoIsLost !!!!!!!! %s is offline and keeps only %d%% of our data' % (
            nameurl.GetName(lost_supplier_idurl), 
            int(offline_suppliers[lost_supplier_idurl] * 100.0)))
        # self.automat('found-one-lost-supplier', lost_supplier_idurl)
        return 'found-one-lost-supplier', lost_supplier_idurl
    # but if we did not saw him for a long time - we do not want him
    if time.time() - ratings.connected_time(lost_supplier_idurl) > 60 * 60 * 24 * 2:
        dhnio.Dprint(2, 'fire_hire.WhoIsLost !!!!!!!! %s is offline and keeps %d%% of our data, but he was online %d hours ago' % (
            nameurl.GetName(lost_supplier_idurl), 
            int(offline_suppliers[lost_supplier_idurl] * 100.0),
            int((time.time() - ratings.connected_time(lost_supplier_idurl)) * 60 * 60),))
        #self.automat('found-one-lost-supplier', lost_supplier_idurl)
        return 'found-one-lost-supplier', lost_supplier_idurl
    dhnio.Dprint(2, 'fire_hire.WhoIsLost not found bad guy!')
    #self.automat('not-found-lost-suppliers')
    return 'not-found-lost-suppliers', ''


def GetLastFireTime():
    return A().lastFireTime




