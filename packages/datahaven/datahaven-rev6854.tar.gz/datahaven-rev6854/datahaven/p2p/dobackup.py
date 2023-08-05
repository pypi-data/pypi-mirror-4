#!/usr/bin/python
#dobackup.py
#
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2012
#    Use of this software constitutes acceptance of the Terms of Use
#      http://datahaven.net/terms_of_use.html
#    All rights reserved.
#
# dobackup is to make one backup.
# backupmanager controls when dobackup is done - sort of a higher level cron type thing.
#
# First we may just do one dhnblock, since man directory zipped is 1/4 MB, much less than 64 MB
#


import os
import sys
import time
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
import backup_db
import backup_monitor

#------------------------------------------------------------------------------

def dobackup(BackupID,
             backuppath,
             backupdirsize,
             recursive_subfolders=True,
             packetResultCallback=None,
             resultDefer=None):
    dhnio.Dprint(4, 'dobackup.dobackup BackupID=%s Path=%s' % (str(BackupID), backuppath))

    if not os.path.exists(backuppath):
        dhnio.Dprint(1, "dobackup.dobackup ERROR with non existant backuppath")
        return fail('dobackup.dobackup with non existant backuppath')

    if contacts.numSuppliers() < eccmap.Current().datasegments:
        dhnio.Dprint(1, "dobackup.dobackup ERROR don't have enough suppliers for current eccmap ")
        return fail("dobackup.dobackup don't have enough suppliers for current eccmap")

    bytesUsed = backup_db.GetTotalBackupsSize()
    bytesNeeded = diskspace.GetBytesFromString(settings.getCentralMegabytesNeeded()) 
    if bytesUsed + backupdirsize >= bytesNeeded:
        backup_monitor.Restart()    

    backuppipe = backup_tar.backuptar(backuppath, recursive_subfolders)
    if backuppipe is None:
        dhnio.Dprint(2, 'dobackup.dobackup WARNING pipe object is None')
        return fail('pipe object is None')

    backuppipe.make_nonblocking()

    dhnio.Dprint(6, 'dobackup.dobackup made a new pipe. pid='+str(backuppipe.pid))

    if resultDefer is None:
        resultDefer = Deferred()
    newbackup = backup.backup(BackupID, backuppipe, resultDeferred=resultDefer)
    newbackup.SetPacketResultCallback(packetResultCallback)
    backup_db.AddRunningBackupObject(BackupID, newbackup)
    backup_db.AddDirBackup(backuppath, BackupID, "in process", backupdirsize, time.time(), 0)
    
    return resultDefer


def shutdown():
    dhnio.Dprint(4, 'dobackup.shutdown ')
    if backup_db.RemoveAllRunningBackupObjects:
        backup_db.RemoveAllRunningBackupObjects()



