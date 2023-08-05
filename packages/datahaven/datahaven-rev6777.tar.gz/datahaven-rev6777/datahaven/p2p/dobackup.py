#!/usr/bin/python
#dobackup.py
#
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2012
#    All rights reserved.
#
# dobackup is to make one backup.
# backupmanager controls when dobackup is done - sort of a higher level cron type thing.
#
# First we may just do one dhnblock, since man directory zipped is 1/4 MB, much less than 64 MB
#


import os
import sys
import datetime


try:
    from twisted.internet import reactor
except:
    sys.exit('Error initializing twisted.internet.reactor in dobackup.py')

from twisted.internet.defer import Deferred, fail


import lib.misc as misc
import lib.dhnio as dhnio
import lib.contacts as contacts
import lib.eccmap as eccmap
import lib.dirsize as dirsize
import lib.settings as settings


import lib.automats as automats
import backup
import backup_tar
#import restore
#import customerservice
import backup_db
#import backup_monitor


#------------------------------------------------------------------------------


def dobackup(BackupID,
             backuppath,
             recursive_subfolders=True,
             packetResultCallback=None,
             resultDefer=None):
    dhnio.Dprint(4, 'dobackup.dobackup BackupID=%s Path=%s' % (str(BackupID), backuppath))

    if not os.path.exists(backuppath):
        dhnio.Dprint(1, "dobackup.dobackup ERROR with non existant backuppath")
        #raise Exception("dobackup.dobackup with non existant backuppath")
        return fail('dobackup.dobackup with non existant backuppath')

    if contacts.numSuppliers() < eccmap.Current().datasegments:
        dhnio.Dprint(1, "dobackup.dobackup ERROR don't have enough suppliers for current eccmap ")
        #raise Exception("dobackup.dobackup don't have enough suppliers for current eccmap ")
        return fail("dobackup.dobackup don't have enough suppliers for current eccmap")

    backuppipe = backup_tar.backuptar(backuppath, recursive_subfolders)
    if backuppipe is None:
        dhnio.Dprint(2, 'dobackup.dobackup WARNING pipe object is None')
        return fail('pipe object is None')

    backuppipe.make_nonblocking()

    dhnio.Dprint(6, 'dobackup.dobackup made a new pipe. pid='+str(backuppipe.pid))

    newbackup = backup.backup(BackupID, backuppipe, resultDeferred=resultDefer)
    newbackup.SetPacketResultCallback(packetResultCallback)
    backup_db.AddRunningBackupObject(BackupID, newbackup)

#    def done(BackupID):
#        dhnio.Dprint(4, 'dobackup.dobackup.done [%s]' % BackupID)
#        backup_db.RemoveRunningBackupObject(BackupID.split(' ')[0])
#        return BackupID
#    newbackup.resultDefer.addBoth(done)

    #return newbackup.resultDefer



def shutdown():
    dhnio.Dprint(4, 'dobackup.shutdown ')
    if backup_db.RemoveAllRunningBackupObjects:
        backup_db.RemoveAllRunningBackupObjects()




#
##------------------------------------------------------------------------------
## Tests
#
#BackupID=""
#trialCallback=""
#
#def trialSuccess(result):
#    dhnio.Dprint(3, "dobackup.trialSuccess starting")
#    result=dhninit.shutdown()
#    if (type(result)==Deferred):
#        result.addCallback(trialSuccess2)
#    else:
#        trialSuccess2()
#
## PREPRO - seems this should not be needed but allowing 3 seconds for dust to settle
#def trialSuccess2():
#    reactor.callLater(3, trialSuccess3)
#
#def trialSuccess3():
#    global trialCallback
#    dhnio.Dprint(3, "dobackup.trialSuccess3 finishing")
#    trialCallback.callback(1)
#
#def trialFailed(result):
#    dhnio.Dprint(1, "dobackup.trialFailed finishing ERROR")
#    trialCallback.errback(1)
#
#def dobackup2():
#    dhninit.init()
#    global BackupID
#    BackupID = "F"+datetime.datetime.now().strftime("%Y%m%d%I%M%S%p")
#    if (dhnio.Linux()):
#        #result=dobackup(BackupID,"/usr/share/man","/tmp/dump1.backup")
#        result=dobackup(BackupID,"/home/vince/man","/tmp/dump1.backup")
#    else:
#        result=dobackup(BackupID,"c:\\work\\projects\\p2p\\old\\","dump1.backup")
#    result.addCallbacks(trialSuccess, trialFailed)
#    global trialCallback
#    trialCallback=Deferred()
#    return(trialCallback)
#
#def dorestore2():
#    dhninit.init()
#    CreatorID =  misc.getLocalID()
###    print "dorestore CreatorID ", CreatorID
#    global BackupID
#    result=restore.restore(BackupID, "restored.tar")
#    ##        result=restore.restore(BackupID, "/tmp/restored.tar")
###    print "dorestore about to return MyDeferred"
#    #return(result.MyDeferred)
#    result.MyDeferred.addCallbacks(trialSuccess, trialFailed)
#    global trialCallback
#    trialCallback=Deferred()
#    return(trialCallback)
#
#def shutdown3(x):
#    dhnio.Dprint(1, "dobackup.shutdown starting")
#    result=dhninit.shutdown()
#    if (type(result)==Deferred):
#        result.addCallback(shutdown2)
#    else:
#        shutdown2()
#
#def shutdown2():
#    dhnio.Dprint(1, "dobackup.shutdown2 starting")
#    reactor.stop()
#
#def calldorestore2(x):
#    dhnio.Dprint(1, "dobackup.calldorestore2 starting")
#    def1=dorestore2()
#    def1.addCallbacks(shutdown, trialFailed)
#
#def main():
#    dhnio.Dprint(1, "dobackup.main starting")
#    def1 = dobackup2()
#    def1.addCallbacks(calldorestore2, trialFailed)       # After backup do restore
#
#if __name__ == '__main__':
#    dhnio.Dprint(1, "dobackup if __main__ was true calling main()")
#    reactor.callLater(1, main)
#    dhnio.Dprint(1, "dobackup if __main__ setup callLater")
#    reactor.run()
#    dhnio.Dprint(1, "dobackup if __main__ after reactor.run")


###  Run this with "tial dobackup"
##class dobackuptest(unittest.TestCase):
##    def test_backup(self):
####        print "timeout was ", self.getTimeout()
##        self.timeout=200000
####        print "timeout is ", self.getTimeout()
##        return(dobackup2())
##
##
##class dorestore(unittest.TestCase):
##    def test_restore(self):
####        print "dobackup dorestore"
##        self.timeout=200000
##        return(dorestore2())

