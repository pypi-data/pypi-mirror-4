#!/usr/bin/python
#backup_db.py
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2012
#    Use of this software constitutes acceptance of the Terms of Use
#      http://datahaven.net/terms_of_use.html
#    All rights reserved.
#
#1)  This tracks backups in metadata/backup_info.xml.
#    It saves the directories to be backed up,
#    the schedule for being backed up if there is one,
#    and then the backups,
#    so when our suppliers say they have files for a particular backup (F20110718100000AM),
#    we know what directory that corresponds to.
#    It should also send the backup_info.xml to the suppliers so that data is backed up.
#    TODO it should encrypt the file and send it out.
#
#2)  Tracks backups in process so we don't try to fix a backup that isn't finished,
#    also so we don't delete a backup in process.



import os
import sys
import time
import locale
import xml.dom.minidom

try:
    from twisted.internet import reactor
except:
    sys.exit('Error initializing twisted.internet.reactor backup_db.py')

import lib.dhnio as dhnio
import lib.misc as misc
import lib.nameurl as nameurl
import lib.settings as settings
import lib.dirsize as dirsize
import lib.commands as commands
import lib.transport_control as transport_control
import lib.dhnpacket as dhnpacket
import lib.contacts as contacts
import lib.dhncrypto as dhncrypto
import lib.schedule as schedule

import backup_db_keeper

#------------------------------------------------------------------------------ 

InitDone = False
_DB = None

#------------------------------------------------------------------------------ 

class _BackupRun:
    def __init__(self, backupID, backupSize=0, backupStatus="", backupStart="", backupFinish=""):
        self.backupID = backupID
        self.backupSize = backupSize
        self.backupStatus = backupStatus
        self.backupStart = backupStart
        self.backupFinish = backupFinish
        if str(self.backupStart) == "":
            self.backupStart = str(time.time())

    def SetStatus(self, backupStatus, backupFinish):
        self.backupStatus = backupStatus
        self.backupFinish = backupFinish

    def GetRunInfo(self):
        return self.backupID, self.backupSize, self.backupStatus, self.backupStart, self.backupFinish

    def Show(self):
        return "  " + self.backupID + "-" + self.backupStatus + "-" + self.backupSize + "-" + self.backupStart + "-" + self.backupFinish

    def ToXML(self):
        runXML =  "        <backupRun>\n"
        runXML += "          <backupId>" + self.backupID + "</backupId>\n"
        runXML += "          <backupSize>" + str(self.backupSize) + "</backupSize>\n"
        runXML += "          <backupStatus>" + self.backupStatus + "</backupStatus>\n"
        runXML += "          <backupStart>" + str(self.backupStart) + "</backupStart>\n"
        runXML += "          <backupFinish>" + str(self.backupFinish) + "</backupFinish>\n"
        runXML += "        </backupRun>\n"
        return runXML


class _BackupSchedule:
    def __init__(self, sched):
        self.schedule = sched

    def SetSchedule(self, sched):
        self.schedule = sched

    def Show(self):
        return self.schedule.description()

    def ToXML(self):
        scheduleXML =  "      <backupSchedule>\n"
        scheduleXML += "        <scheduleType>" + self.schedule.type + "</scheduleType>\n"
        scheduleXML += "        <scheduleTime>" + self.schedule.daytime + "</scheduleTime>\n"
        scheduleXML += "        <scheduleInterval>" + self.schedule.interval + "</scheduleInterval>\n"
        scheduleXML += "        <intervalDetails>" + self.schedule.details + "</intervalDetails>\n"
        scheduleXML += "      </backupSchedule>\n"
        return scheduleXML


class _BackupDirectory:
    def __init__(self, dirName, backupSubdirectories=True):
        self.dirName = dirName
        self.backupSubdirectories = backupSubdirectories # do backup of subdirectories
        self.schedule = None 
        self.backupRuns = [] # an array of _BackupRun in order of time, oldest to newest
        self.runningBackup = False # True if some backup of this folders is running 

    def AddBackupRun(self, backupID, backupSize, backupStatus, backupStart, backupFinish):
        self.backupRuns.append(_BackupRun(backupID, backupSize, backupStatus, backupStart, backupFinish))
        if backupStatus in ['in process', 'sending']:
            self.runningBackup = True

    def DeleteDirBackup(self, backupID):
        delBackupRun = []
        for backupRun in self.backupRuns:
            if backupRun.backupID == backupID:
                delBackupRun.append(backupRun)
        for backupRun in delBackupRun:
            self.backupRuns.remove(backupRun)
        del delBackupRun

    def GetLastRunInfo(self):
        if len(self.backupRuns)>0:
            return self.backupRuns[-1].GetRunInfo()
        else:
            return "", "0.0", "(none)", str(time.time()), ""

    def GetDirBackupIds(self):
        backupIds = []
        for backupRun in self.backupRuns:
            backupIds.append(str(backupRun.backupID))
        return backupIds

    def GetDirectorySubfoldersInclude(self):
        return self.backupSubdirectories

    def SetDirectorySubfoldersInclude(self, backupSubdirectories):
        if backupSubdirectories == False:
            self.backupSubdirectories = False
        else:
            self.backupSubdirectories = True

    def IsBackupRunning(self):
        return self.runningBackup

    def SetBackupStatus(self, backupID, backupStatus, backupFinish):
        for backupRun in self.backupRuns:  #TODO, do we need backupID at all?  Just set backupRuns[-1] ?
            if backupRun.backupID == backupID:
                dhnio.Dprint(6, 'backup_db.SetBackupStatus %s %s %s' % (backupID, backupStatus, str(backupFinish)))
                backupRun.SetStatus(backupStatus, backupFinish)
                self.runningBackup = False
                return

    def GetDirectoryInfo(self):
        if len(self.backupRuns) > 0:
            mostRecentBackupId = ""
            totalSize = 0.0
            mostRecentStatus = ""
            for backupRun in self.backupRuns:
                backupID, backupSize, backupStatus, backupStart, backupFinish = backupRun.GetRunInfo()
                totalSize += int(backupSize)
                mostRecentBackupId = backupID
                mostRecentStatus = backupStatus
            return mostRecentBackupId, totalSize, mostRecentStatus
        else:
            return '', 0, ''

    def SetDirSchedule(self, schedule):
        if self.schedule == None:
            self.schedule = _BackupSchedule(schedule)
        else:
            self.schedule.SetSchedule(schedule)

    def Show(self):
        dirShow =  self.dirName + "\n"
        if self.schedule:
            dirShow = dirShow + self.schedule.Show() + "\n"
        for backupRun in self.backupRuns:
            dirShow = dirShow + backupRun.Show() + "\n"
        return dirShow

    def ToXML(self):
        dirXML =  "    <backupDirectory>\n"
        dirXML += "      <directoryName>" + self.dirName + "</directoryName>\n"
        dirXML += "      <backupSubdirectories>" + str(self.backupSubdirectories) + "</backupSubdirectories>\n"
        if self.schedule:
            dirXML += self.schedule.ToXML()
        if len(self.backupRuns) > 0:
            dirXML += "      <directoryBackups>\n"
            for backupRun in self.backupRuns:
                dirXML += backupRun.ToXML()
            dirXML += "      </directoryBackups>\n"
        dirXML += "    </backupDirectory>\n"
        return dirXML


class _BackupDB:
    def __init__(self):
        self.backupDirs = {}
        self.deletedBackups = []
        self.revisionNumber = 0
        self.currentlyRunningBackups = {}
        self._xmlFile = settings.BackupInfoFileFullPath()
        self._maxDeleted = settings.MaxDeletedBackupIDsToKeep()
        self._loading = False

    def BackupDirs(self):
        return self.backupDirs

    def AskSizeForAllDirs(self):
        for backupDir in self.backupDirs.keys():
            dirsize.ask(backupDir)

    def _GetText(self, nodelist): # get text from DOM elements
        rc = ""
        for node in nodelist:
            if node.hasChildNodes():
                rc = rc + self._GetText(node.childNodes)
            elif node.nodeType == node.TEXT_NODE: # TEXT_NODE is node type 3
                rc = rc + node.data.strip()
        return rc

    def InboxBackupInfoPacket(self, packet):
        try:
            xmlSrc = packet.Payload
            xmlDom = xml.dom.minidom.parseString(xmlSrc)
            rootNode = xmlDom.documentElement
        except:
            dhnio.Dprint(4, 'backup_db.InboxBackupInfoPacket ERROR reading xml source from %s' + packet.RemoteID)
            return
        revisionNumber = misc.ToInt(self._GetText(rootNode.getElementsByTagName('revisionNumber')), 0)
        if self.revisionNumber < revisionNumber:
            self.LoadXML(rootNode)
            self.Write()
        backup_db_keeper.A('incoming-db-info', packet)

    def ToXML(self):
        self.CommandLog("ToXML")
        dbXML = ''
        dbXML += '<?xml version="1.0" encoding="%s" ?>\n' % locale.getpreferredencoding()
        dbXML += '<backupData>\n'
        dbXML += '  <revisionNumber>%d</revisionNumber>\n' % self.revisionNumber 
        dbXML += '  <backupDirectories>\n'
        for dirName in self.backupDirs:
            dbXML += self.backupDirs[dirName].ToXML()
        dbXML += '  </backupDirectories>\n'
        dbXML += '  <deletedBackups>\n'
        for backupID in self.deletedBackups[0-self._maxDeleted:]:
            dbXML += '    <deletedBackup>\n'
            dbXML += '      <deletedBackupId>' + backupID + '</deletedBackupId>\n'
            dbXML += '    </deletedBackup>\n'
        dbXML += '  </deletedBackups>\n'
        dbXML += '</backupData>\n'
        return dbXML

    def LoadXML(self, rootNode):
        self.revisionNumber = misc.ToInt(self._GetText(rootNode.getElementsByTagName('revisionNumber')), 0)
        backupDirs = rootNode.getElementsByTagName("backupDirectory")
        for backupDir in backupDirs: # DOM Elements
            dirName = self._GetText(backupDir.getElementsByTagName("directoryName"))
            backupSubdirectories = 'true' == str(self._GetText(backupDir.getElementsByTagName("backupSubdirectories"))).lower().strip()
            self.AddDirectory(dirName, backupSubdirectories)
            for sched in backupDir.getElementsByTagName("backupSchedule"):
                self.SetDirSchedule(
                    dirName, 
                    schedule.Schedule( 
                        typ = str(self._GetText(sched.getElementsByTagName("scheduleType"))), 
                        daytime = str(self._GetText(sched.getElementsByTagName("scheduleTime"))), 
                        interval = str(self._GetText(sched.getElementsByTagName("scheduleInterval"))), 
                        details = str(self._GetText(sched.getElementsByTagName("intervalDetails")))),)
            for backupRun in backupDir.getElementsByTagName("backupRun"):
                self.AddDirBackup(
                    dirName, 
                    str(self._GetText(backupRun.getElementsByTagName("backupId"))), 
                    # when we loading backup_db from file or from remote supplier
                    # we do not care about backups statuses, only need to know backupID
                    # str(self._GetText(backupRun.getElementsByTagName("backupStatus"))),
                    'done', 
                    misc.ToInt(self._GetText(backupRun.getElementsByTagName("backupSize"))), 
                    misc.ToFloat(self._GetText(backupRun.getElementsByTagName("backupStart"))), 
                    misc.ToFloat(self._GetText(backupRun.getElementsByTagName("backupFinish"))),)
        deletedBackups = rootNode.getElementsByTagName("deletedBackup")
        for deletedBackup in deletedBackups:
            backupID = str(self._GetText(deletedBackup.getElementsByTagName("deletedBackupId")))
            self.deletedBackups.append(backupID)
    
    def Clear(self):
        self.backupDirs.clear()
        self.deletedBackups = []
        self.revisionNumber = 0

    def Write(self):
        try:
            src = self.ToXML()
            f = open(self._xmlFile+"new.xml", "w")
            f.write(src)
            f.close()
            try:
                xmlDOM = xml.dom.minidom.parse(self._xmlFile+"new.xml")
                # make sure we are saving something valid
            except:
                dhnio.Dprint(2, "backup_db.Write ERROR new file is not a valid XML file")
                dhnio.DprintException()
                os.remove(self._xmlFile+'new.xml')
                return
            if dhnio.Windows() and os.path.exists(self._xmlFile):
                os.remove(self._xmlFile)
            os.rename(self._xmlFile+"new.xml", self._xmlFile)
        except:
            dhnio.Dprint(2, "backup_db.Write ERROR unable to save new XML file")
            dhnio.DprintException()
        
    def Save(self):
        if self._loading:
            return
        self.revisionNumber += 1
        self.Write()
        backup_db_keeper.A('restart')

    def Load(self):
        if os.path.exists(self._xmlFile):
            self._loading = True
            try:
                xmlDOM = xml.dom.minidom.parse(self._xmlFile)
            except:
                dhnio.Dprint(2, "backup_db.Load ERROR not a valid XML file")
                return
            rootNode = xmlDOM.documentElement
            self.Clear()
            self.LoadXML(rootNode)
            self._loading = False

    # used during developement to debug some stuff
    def CommandLog(self, command):
        dhnio.Dprint(6, 'backup_db: ' + str(command))

    #--- begin of signing/encryption section, not yet active ---
    
    def SaveAddon(self):
        SessionKey = dhncrypto.NewSessionKey()
        # SessionKeyType = dhncrypto.SessionKeyType()
        # LocalID = misc.getLocalIdentity().getIDURL()
        Data = dhnio.ReadBinaryFile(self._xmlFile)
        DataLonger = misc.RoundupString(Data, 24)
        self.EncryptedData = dhncrypto.EncryptWithSessionKey(SessionKey, DataLonger)
        self.Signature = self.GenerateSignature()  # usually just done at packet creation

    def SessionKey(self):
        return dhncrypto.DecryptLocalPK(self.EncryptedSessionKey)

    def GenerateHashBase(self):
        sep = "::::"
        # PREPRO needs to have all fields and separator
        StringToHash = self.CreatorID + sep + self.SessionKeyType + sep + self.EncryptedSessionKey + sep + self.Length + sep + self.EncryptedData
        return StringToHash

    def GenerateHash(self):
        return dhncrypto.Hash(self.GenerateHashBase())

    def GenerateSignature(self):
        return dhncrypto.Sign(self.GenerateHash())
    
    #--- end of signing/encryption section, not yet active ---

    # dirName should be unicode!!!
    def AddDirectory(self, dirName, recursive=True):
        if not self.backupDirs.has_key(dirName):
            self.CommandLog("AddDirectory made new entry [%s]" % dirName)
            self.backupDirs[dirName] = _BackupDirectory(dirName, recursive)
        else:
            self.CommandLog("AddDirectory already exist {%s}" % dirName)

    def DeleteDirectory(self, dirName):
        self.CommandLog("DelDirectory " + dirName)
        for dbDir in self.backupDirs.keys():
            if os.path.abspath(dirName) == os.path.abspath(dbDir):
                for backupRun in self.backupDirs[dbDir].backupRuns:
                    if backupRun.backupID not in self.deletedBackups:
                        self.deletedBackups.append(backupRun.backupID)
                del self.backupDirs[dbDir]

    def CheckDirectory(self, dirName):
        if self.backupDirs.has_key(dirName):
            return True
        else:
            return False

    def GetBackupDirectories(self):
        backupDirectories = self.backupDirs.keys()
        # backupDirectories.sort()
        return backupDirectories

    def GetDirectoryInfo(self, dirName):
        if self.backupDirs.has_key(dirName):
            return self.backupDirs[dirName].GetDirectoryInfo()
        return '', 0, ''

    def AddDirBackup(self, dirName, backupID, backupStatus="", backupSize=0, backupStart=0, backupFinish=0, ):
        self.CommandLog("AddDirBackup [%s] %s %s %d %d %d" % (dirName, backupID, backupStatus, backupSize, backupStart, backupFinish,))
        if not self.backupDirs.has_key(dirName):
            self.backupDirs[dirName] = _BackupDirectory(dirName)
        self.backupDirs[dirName].AddBackupRun(backupID, backupSize, backupStatus, backupStart, backupFinish)

    def DeleteDirBackup(self, backupID):
        self.CommandLog("DeleteDirBackup " + backupID)
        dirName = self.GetDirectoryFromBackupId(backupID)
        if self.backupDirs.has_key(dirName):
            self.backupDirs[dirName].DeleteDirBackup(backupID)
        if backupID not in self.deletedBackups:
            self.deletedBackups.append(backupID)

    def IsDeleted(self, backupID):
        if backupID in self.deletedBackups:
            return True
        else:
            return False

    def GetDirLastBackup(self, dirName):
        if self.backupDirs.has_key(dirName):
            if len(self.backupDirs[dirName].backupRuns) > 0:
                lastBackup = self.backupDirs[dirName].backupRuns[-1]
                return lastBackup.backupID, lastBackup.backupSize, lastBackup.backupStatus, lastBackup.backupStart, lastBackup.backupFinish
        return "", 0, "", 0, 0

    def GetDirBackupIds(self, dirName):
        if self.backupDirs.has_key(dirName):
            return self.backupDirs[dirName].GetDirBackupIds()
        else:
            return []

    def SetBackupStatus(self, dirName, backupID, backupStatus, backupFinish):
        self.CommandLog("SetBackupStatus " + dirName + " " + backupID + " " + backupStatus + " " + backupFinish)
        if self.backupDirs.has_key(dirName):
            self.backupDirs[dirName].SetBackupStatus(backupID, backupStatus, backupFinish)

    def AbortDirectoryBackup(self, dirName):
        if self.backupDirs.has_key(dirName):
            self.backupDirs[dirName].runningBackup = False

    def GetLastRunInfo(self, dirName):
        return self.backupDirs[dirName].GetLastRunInfo()

    def IsBackupRunning(self, dirName):
        if self.backupDirs.has_key(dirName):
            return self.backupDirs[dirName].IsBackupRunning()
        return False

    def SetDirSchedule(self, dirName, sched):
        if self.backupDirs.has_key(dirName):
            self.CommandLog("SetDirSchedule %s %s %s %s %s" % (dirName, sched.type, sched.daytime, sched.interval, sched.details))
            self.backupDirs[dirName].SetDirSchedule(sched)

    def GetDirSchedule(self, dirName):
        if self.backupDirs.has_key(dirName):
            if self.backupDirs[dirName].schedule != None:
                return self.backupDirs[dirName].schedule.schedule
        return None

    def GetDirectorySubfoldersInclude(self, dirName):
        if self.backupDirs.has_key(dirName):
            return self.backupDirs[dirName].GetDirectorySubfoldersInclude()
        return True

    def SetDirectorySubfoldersInclude(self, dirName, backupSubfolders):
        if self.backupDirs.has_key(dirName):
            self.backupDirs[dirName].SetDirectorySubfoldersInclude(backupSubfolders)

    def GetDirectoryFromBackupId(self, backupID):
        for dirName in self.backupDirs.keys():
            for backupRun in self.backupDirs[dirName].backupRuns:
                if backupRun.backupID == backupID:
                    return dirName
        return ''

    def GetBackupIdRunInfo(self, backupID):
        for dirName in self.backupDirs.keys():
            for backupRun in self.backupDirs[dirName].backupRuns:
                if backupRun.backupID == backupID:
                    return backupRun.GetRunInfo()
        return None
    
    def GetBackupsByDateTime(self, reverse=False):
        d = {}
        for dirName in self.backupDirs.keys():
            for backupRun in self.backupDirs[dirName].backupRuns:
                d[backupRun.backupID] = (backupRun.backupID, dirName, backupRun.backupSize, backupRun.backupStatus)
        l = []
        for backupID in misc.sorted_backup_ids(d.keys(), reverse):
            l.append(d[backupID])
        d.clear()
        return l
    
    def GetBackupsByFolder(self):
        result = []
        for dirName in self.backupDirs.keys():
            dirBackupsSize = 0
            backupRuns = []
            for backupRun in self.backupDirs[dirName].backupRuns:
                backupRuns.append(backupRun)
                dirBackupsSize += backupRun.backupSize
            recentBackupID = '' if len(backupRuns) == 0 else backupRuns[0].backupID 
            result.append((dirName, backupRuns, dirBackupsSize, self.backupDirs[dirName].runningBackup, recentBackupID))
        return result 

    def Show(self):
        dbList = ""
        for dirName in self.backupDirs:
            dbList = dbList + self.backupDirs[dirName].Show()
        return dbList

    def GetBackupIds(self, full_info_please=False):
        backupIds = []
        for dirName in self.backupDirs:
            for backupRun in self.backupDirs[dirName].backupRuns:
                if full_info_please:
                    backupIds.append((str(backupRun.backupID), dirName, backupRun.backupSize, backupRun.backupStatus))
                else:
                    backupIds.append(str(backupRun.backupID))
        return misc.sorted_backup_ids(backupIds)

    def GetTotalBackupsSize(self):
        backupsSize = 0
        for dirName in self.backupDirs:
            for backupRun in self.backupDirs[dirName].backupRuns:
                backupsSize += int(backupRun.backupSize)
        return backupsSize

    # the backup objects are backup.backup's
    def AddRunningBackupObject(self, backupID, backupObject):
        if not self.currentlyRunningBackups.has_key(backupID):
            self.currentlyRunningBackups[backupID] = backupObject
            
    def GetRunningBackupObject(self, backupID):
        return self.currentlyRunningBackups.get(backupID, None)

    def RemoveRunningBackupObject(self, backupID):
        if self.currentlyRunningBackups.has_key(backupID):
            del self.currentlyRunningBackups[backupID]

    def AbortRunningBackup(self, backupID):
        if self.currentlyRunningBackups.has_key(backupID):
            self.currentlyRunningBackups[backupID].abort()
        
    def RemoveAllRunningBackupObjects(self):
        self.currentlyRunningBackups.clear()

    def ShowRunningBackups(self):
        return self.currentlyRunningBackups.keys()

    def HasRunningBackup(self):
        if len(self.currentlyRunningBackups.keys()) > 0:
            return True
        return False
    
#------------------------------------------------------------------------------ 

def BackupDirs():
    return db().BackupDirs()

def ToXML():
    return db().ToXML()

def Save():
    return db().Save()

def InboxBackupInfoPacket(packet):
    return db().InboxBackupInfoPacket(packet)

def AddDirectory(dirName, recursive=True):
    return db().AddDirectory(dirName, recursive)
    
def DeleteDirectory(dirName):
    return db().DeleteDirectory(dirName)
    
def CheckDirectory(dirName):
    return db().CheckDirectory(dirName)
    
def GetBackupDirectories():
    return db().GetBackupDirectories()
    
def GetDirectoryInfo(dirName):
    return db().GetDirectoryInfo(dirName)

def AddDirBackup(dirName, backupID, backupStatus="", backupSize=0, backupStart=0, backupFinish=0):
    return db().AddDirBackup(dirName, backupID, backupStatus, backupSize, backupStart, backupFinish)
    
def DeleteDirBackup(backupID):
    return db().DeleteDirBackup(backupID)
    
def IsDeleted(backupID):
    return db().IsDeleted(backupID)
    
def SetBackupStatus(dirName, backupID, backupStatus, backupFinish):
    return db().SetBackupStatus(dirName, backupID, backupStatus, backupFinish)
    
def AbortDirectoryBackup(dirName):
    return db().AbortDirectoryBackup(dirName)
    
def GetLastRunInfo(dirName):
    return db().GetLastRunInfo(dirName)
    
def IsBackupRunning(dirName):
    return db().IsBackupRunning(dirName)

def GetSchedule(dirName):
    return db().GetDirSchedule(dirName)

def SetSchedule(dirName, sched):
    return db().SetDirSchedule(dirName, sched)

def GetLastRun(dirName):
    return db().GetDirLastBackup(dirName)

def GetDirBackupIds(dirName):
    return db().GetDirBackupIds(dirName)

def GetBackupIds(full_info_please=False):
    return db().GetBackupIds(full_info_please)
    
def GetTotalBackupsSize():
    return db().GetTotalBackupsSize()

def GetDirectoryFromBackupId(backupID):
    return db().GetDirectoryFromBackupId(backupID)

def GetDirectorySubfoldersInclude(dirName):
    return db().GetDirectorySubfoldersInclude(dirName)

def SetDirectorySubfoldersInclude(dirName, backupSubfolders):
    return db().SetDirectorySubfoldersInclude(dirName, backupSubfolders)

def GetBackupIdRunInfo(backupID):
    return db().GetBackupIdRunInfo(backupID)

def GetBackupsByDateTime(reverse=False):
    return db().GetBackupsByDateTime(reverse)
    
def GetBackupsByFolder():
    return db().GetBackupsByFolder()

def AddRunningBackupObject(backupID, backupObject):
    return db().AddRunningBackupObject(backupID, backupObject)

def GetRunningBackupObject(backupID):
    return db().GetRunningBackupObject(backupID)

def RemoveRunningBackupObject(backupID):
    return db().RemoveRunningBackupObject(backupID)

def RemoveAllRunningBackupObjects():
    return db().RemoveAllRunningBackupObjects()

def HasRunningBackup():
    return db().HasRunningBackup()

def ShowRunningBackups():
    return db().ShowRunningBackups()

def AbortRunningBackup(backupID):
    return db().AbortRunningBackup(backupID)

#------------------------------------------------------------------------------ 

def db():
    global _DB
    if _DB is None:
        _DB = _BackupDB()
    return _DB

def init():
    _local_backup_db = db()

    global InitDone
    if InitDone:
        return

    dhnio.Dprint(4,"backup_db.init")

    _local_backup_db.Load()
    _local_backup_db.AskSizeForAllDirs()

    #init state
    InitDone = True


#------------------------------------------------------------------------------ 

if __name__ == "__main__":
    init()
    import pprint
    pprint.pprint(GetBackupIds())
    pprint.pprint(GetBackupDirectories())
#    newdir = unicode(sys.argv[1])
#    print 'want to add:', newdir
##    AddDirBackup(newdir, "F3000000000AM", "done", "12344321", "1234554321.11", "1234554323.11")
#    AddDirectory(newdir)
##    DeleteDirectory(newdir)
#    print ToXML()
##    print GetDirectoryFromBackupId("F3000000000AM")
##    print CheckDirectory(newdir)
    #_local_backup_db.Save()
