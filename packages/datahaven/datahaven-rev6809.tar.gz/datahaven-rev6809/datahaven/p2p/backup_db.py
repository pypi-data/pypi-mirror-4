#!/usr/bin/python
#backup_db.py
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2012
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
#from xml.dom import Node

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
        runXML =  "      <backupRun>\n"
        runXML += "        <backupId>" + self.backupID + "</backupId>\n"
        runXML += "        <backupSize>" + str(self.backupSize) + "</backupSize>\n"
        runXML += "        <backupStatus>" + self.backupStatus + "</backupStatus>\n"
        runXML += "        <backupStart>" + str(self.backupStart) + "</backupStart>\n"
        runXML += "        <backupFinish>" + str(self.backupFinish) + "</backupFinish>\n"
        runXML += "      </backupRun>\n"
        return runXML


class _BackupSchedule:
    def __init__(self, sched):
        self.schedule = sched
#        self.scheduleType = scheduleType
#        self.scheduleTime = scheduleTime
#        self.scheduleInterval = scheduleInterval
#        self.intervalDetails = intervalDetails

    def SetSchedule(self, sched):
        self.schedule = sched
#        self.scheduleType = scheduleType
#        self.scheduleTime = scheduleTime
#        self.scheduleInterval = scheduleInterval
#        self.intervalDetails = intervalDetails

    def Show(self):
#        return "  "  + self.scheduleType + "-" + self.scheduleTime + "-" + str(self.scheduleInterval) + "-" + self.intervalDetails
        return self.schedule.description()

    def ToXML(self):
#        scheduleXML =  "    <backupSchedule>\n"
#        scheduleXML += "      <scheduleType>" + str(self.scheduleType) + "</scheduleType>\n"
#        scheduleXML += "      <scheduleTime>" + self.scheduleTime + "</scheduleTime>\n"
#        scheduleXML += "      <scheduleInterval>" + str(self.scheduleInterval) + "</scheduleInterval>\n"
#        scheduleXML += "      <intervalDetails>" + self.intervalDetails + "</intervalDetails>\n"
#        scheduleXML += "    </backupSchedule>\n"
        scheduleXML =  "    <backupSchedule>\n"
        scheduleXML += "      <scheduleType>" + self.schedule.type + "</scheduleType>\n"
        scheduleXML += "      <scheduleTime>" + self.schedule.daytime + "</scheduleTime>\n"
        scheduleXML += "      <scheduleInterval>" + self.schedule.interval + "</scheduleInterval>\n"
        scheduleXML += "      <intervalDetails>" + self.schedule.details + "</intervalDetails>\n"
        scheduleXML += "    </backupSchedule>\n"
        return scheduleXML


class _BackupDirectory:
    def __init__(self, dirName, backupSubdirectories=True):
        self.dirName = dirName
        self.backupSubdirectories = backupSubdirectories # do subdirectories
        self.schedule = None
        self.backupRuns = []  # an array of _BackupRun in order of time, oldest to newest
        self.backupObject = None
        self.runningBackup = False

    def AddBackupRun(self, backupID, backupSize, backupStatus, backupStart, backupFinish, initialLoad=False):
        if initialLoad and backupStatus in ['in process', 'sending']:
            self.backupRuns.append(_BackupRun(backupID, backupSize, "unknown", backupStart, backupFinish))
        else:
            self.backupRuns.append(_BackupRun(backupID, backupSize, backupStatus, backupStart, backupFinish))
            if backupStatus in ['in process', 'sending']:
                self.runningBackup = True

    def DeleteDirBackup(self, backupID):
        delBackupRun = None
        for backupRun in self.backupRuns:
            if backupRun.backupID == backupID:
                delBackupRun = backupRun
        if delBackupRun != None:
            self.backupRuns.remove(delBackupRun)

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
        dirXML =  "  <backupDirectory>\n"
        dirXML += "    <directoryName>" + self.dirName + "</directoryName>\n"
        dirXML += "    <backupSubdirectories>" + str(self.backupSubdirectories) + "</backupSubdirectories>\n"
        if self.schedule:
            dirXML += self.schedule.ToXML()
        if len(self.backupRuns) > 0:
            dirXML += "    <directoryBackups>\n"
            for backupRun in self.backupRuns:
                dirXML += backupRun.ToXML()
            dirXML += "    </directoryBackups>\n"
        dirXML += "  </backupDirectory>\n"
        return dirXML


class _BackupDB:
    def __init__(self):
        self.backupDirs = {}
        self.currentlyRunningBackups = {}
        #self._oldBackupsDir = os.path.join(os.path.expanduser("~"),"datahavennet","backups")
        self._xmlFile = settings.BackupInfoFileFullPath()
        self.deletedBackups = []
        self._maxDeleted = 50 # how many deleted backupIDs do we want to hold on to?
        self.localID = misc.getLocalID()
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

    def _LoadXML(self):
        try:
            xmlDOM = xml.dom.minidom.parse(self._xmlFile)
        except:
            dhnio.Dprint(2, "backup_db._LoadXML ERROR not a valid XML file")
            return

        rootNode = xmlDOM.documentElement
        backupDirs = rootNode.getElementsByTagName("backupDirectory")
        for backupDir in backupDirs: # DOM Elements
            self._LoadDir(backupDir)
        deletedBackups = rootNode.getElementsByTagName("deletedBackup")
        for deletedBackup in deletedBackups:
            self._LoadDeleted(deletedBackup)
            #self.deletedBackups.append(self._GetText(deletedBackup))

    def _LoadDeleted(self, deletedBackup): # backupDir is some DOM Elements
        backupID = str(self._GetText(deletedBackup.getElementsByTagName("deletedBackupId")))
        #print "backupID="+backupID
        if backupID not in self.deletedBackups:
            self.deletedBackups.append(backupID)

    def _LoadDir(self, backupDir): # backupDir is some DOM Elements
        dirName = str(self._GetText(backupDir.getElementsByTagName("directoryName")))
        backupSubdirectories = str(self._GetText(backupDir.getElementsByTagName("backupSubdirectories")))
        if backupSubdirectories == "False":
            self.AddDirectory(dirName, False, initialLoad=True)
        else:
            self.AddDirectory(dirName, True, initialLoad=True)
        for schedule in backupDir.getElementsByTagName("backupSchedule"):
            self._LoadSchedule(dirName, schedule) # schedule is some DOM elements
        for backupRun in backupDir.getElementsByTagName("backupRun"):
            self._LoadBackupRun(dirName, backupRun) # backupRun is some DOM elements)

    def _LoadBackupRun(self, dirName, backupRun):
        self.AddDirBackup(dirName, 
                          str(self._GetText(backupRun.getElementsByTagName("backupId"))), \
                          str(self._GetText(backupRun.getElementsByTagName("backupStatus"))), \
                          misc.ToInt(self._GetText(backupRun.getElementsByTagName("backupSize"))), \
                          misc.ToFloat(self._GetText(backupRun.getElementsByTagName("backupStart"))), \
                          misc.ToFloat(self._GetText(backupRun.getElementsByTagName("backupFinish"))), \
                          initialLoad=True)

    def _LoadSchedule(self, dirName, sched):
        self.SetDirSchedule(dirName, schedule.Schedule( 
                            typ = str(self._GetText(sched.getElementsByTagName("scheduleType"))), 
                            daytime = str(self._GetText(sched.getElementsByTagName("scheduleTime"))), 
                            interval = str(self._GetText(sched.getElementsByTagName("scheduleInterval"))), 
                            details = str(self._GetText(sched.getElementsByTagName("intervalDetails")))))

    def Save(self):
##        print 'Save'
        if self._loading:
            return
        try:
            src = self.ToXML()
            f = open(self._xmlFile+"new.xml", "w")
            f.write(src)
            f.close()
            try:
                xmlDOM = xml.dom.minidom.parse(self._xmlFile+"new.xml")
                # make sure we are saving something valid
            except:
                dhnio.Dprint(2, "backup_db.Save ERROR new file is not a valid XML file")
                dhnio.DprintException()
                return

            if dhnio.Windows() and os.path.exists(self._xmlFile):
                os.remove(self._xmlFile)
            os.rename(self._xmlFile+"new.xml",self._xmlFile)

            #f = open(str(time.time())+"backup.xml","w") # used during development to debug some stuff
            #f.write(self.ToXML())
            #f.close()
            Payload = dhnio.ReadBinaryFile(self._xmlFile)
##            for supplierId in contactsdb.suppliers():
            def _send( Payload, localID):
                for supplierId in contacts.getSupplierIDs():
                    dhnio.Dprint(8, "backup_db.Save backing up " + settings.BackupInfoFileName() + " to " + nameurl.GetName(supplierId))
                    newpacket = dhnpacket.dhnpacket(commands.Data(), localID, localID, settings.BackupInfoFileName(), Payload, supplierId)
                    transport_control.outboxAck(newpacket)
            reactor.callInThread(_send, Payload, self.localID)
        except:
            dhnio.Dprint(2, "backup_db.Save ERROR unable to save new XML file")
            dhnio.DprintException()

    def Load(self):
        #if os.path.exists(self._oldBackupsDir):
        #    self._ConvertOld()
        #    self.Save()
        #    os.rename(self._oldBackupsDir,self._oldBackupsDir+"_old")
        #elif
        if os.path.exists(self._xmlFile):
            self._loading = True
            self._LoadXML()
            self._loading = False
        #print self.ToXML()
        #self.Save()

    # used during developement to debug some stuff
    def CommandLog(self, command):
        dhnio.Dprint(6, 'backup_db: ' + str(command))
        #f = open("backup_commands.log", "a")
        #f.write(str(time.time()) + " " + command+"\n")
        #f.close()

    # begin of signing/encryption section, not yet active
    def SaveAddon(self):
        SessionKey = dhncrypto.NewSessionKey()
#        SessionKeyType = dhncrypto.SessionKeyType()
#        LocalID = misc.getLocalIdentity().getIDURL()
        Data = dhnio.ReadBinaryFile(self._xmlFile)
        DataLonger = misc.RoundupString(Data,24)
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
## end of signing/encryption section, not yet active

    def AddDirectory(self, dirName, recursive=True, initialLoad=False):
        self.CommandLog("AddDirectory [%s] %s %s" % (dirName, str(recursive), str(initialLoad)))
        if not self.backupDirs.has_key(dirName):
            self.backupDirs[dirName] = _BackupDirectory(dirName, recursive)
        if not initialLoad:
            self.Save()

    def DeleteDirectory(self, dirName):
        #dhnio.Dprint(8, 'backup_db.DeleteDirectory ' + dirName)
        self.CommandLog("DelDirectory " + dirName)
        for dbDir in self.backupDirs.keys():
            if os.path.abspath(dirName) == os.path.abspath(dbDir):
            #if self.backupDirs.has_key(dirName):
                for backupRun in self.backupDirs[dbDir].backupRuns:
                    if backupRun.backupID not in self.deletedBackups:
                        self.deletedBackups.append(backupRun.backupID)
                del self.backupDirs[dbDir]
        self.Save()

    def CheckDirectory(self, dirName):
        #self.CommandLog("CheckDirectory " + dirName)
        if self.backupDirs.has_key(dirName):
            return True
        else:
            return False

    def GetBackupDirectories(self):
        #self.CommandLog("Get backup directories")
        backupDirectories = self.backupDirs.keys()
        backupDirectories.sort()
        return backupDirectories

    def GetDirectoryInfo(self, dirName):
        #self.CommandLog("GetDirectoryInfo " + dirName)
        if self.backupDirs.has_key(dirName):
            return self.backupDirs[dirName].GetDirectoryInfo()
        return '', 0, ''

    def AddDirBackup(self, dirName, backupID, backupStatus="", backupSize=0, backupStart=0, backupFinish=0, initialLoad=False):
        self.CommandLog("AddDirBackup [%s] %s %s %d %d %d %s" % (dirName, backupID, backupStatus, backupSize, backupStart, backupFinish, str(initialLoad)))
        if not self.backupDirs.has_key(dirName):
            self.backupDirs[dirName] = _BackupDirectory(dirName)
        self.backupDirs[dirName].AddBackupRun(backupID, backupSize, backupStatus, backupStart, backupFinish, initialLoad)
        if not initialLoad:
            self.Save()

    def DeleteDirBackup(self, backupID):
        self.CommandLog("DeleteDirBackup " + backupID)
        dirName = self.GetDirectoryFromBackupId(backupID)
        if self.backupDirs.has_key(dirName):
            self.backupDirs[dirName].DeleteDirBackup(backupID)
        if backupID not in self.deletedBackups:
            self.deletedBackups.append(backupID)
        self.Save()

    def IsDeleted(self, backupID):
        #self.CommandLog("IsDeleted " + backupID)
        if backupID in self.deletedBackups:
            return True
        else:
            return False

    def GetDirLastBackup(self, dirName):
        #self.CommandLog("GetDirLastBackup " + dirName)
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
            self.Save()

    def AbortDirectoryBackup(self, dirName):
        if self.backupDirs.has_key(dirName):
            self.backupDirs[dirName].runningBackup = False

    def GetLastRunInfo(self, dirName):
        #self.CommandLog("GetLastRunInfo " + dirName)
        return self.backupDirs[dirName].GetLastRunInfo()

    def IsBackupRunning(self, dirName):
        #self.CommandLog("GetDirectoryInfo " + dirName)
        if self.backupDirs.has_key(dirName):
            return self.backupDirs[dirName].IsBackupRunning()
        return False

    #def SetDirSchedule(self, dirName, scheduleType, scheduleTime, scheduleInverval, intervalDetails):
    def SetDirSchedule(self, dirName, sched):
        if self.backupDirs.has_key(dirName):
            self.CommandLog("SetDirSchedule %s %s %s %s %s" % (dirName, sched.type, sched.daytime, sched.interval, sched.details))
            self.backupDirs[dirName].SetDirSchedule(sched)
            self.Save()

    def GetDirSchedule(self, dirName):
        #self.CommandLog("GetDirSchedule" + dirName)
        if self.backupDirs.has_key(dirName):
            if self.backupDirs[dirName].schedule != None:
#                return self.backupDirs[dirName].schedule.scheduleType, self.backupDirs[dirName].schedule.scheduleTime, \
#                        self.backupDirs[dirName].schedule.scheduleInterval, self.backupDirs[dirName].schedule.intervalDetailsk
                return self.backupDirs[dirName].schedule.schedule
        return None

    def GetDirectorySubfoldersInclude(self, dirName):
        if self.backupDirs.has_key(dirName):
            return self.backupDirs[dirName].GetDirectorySubfoldersInclude()
        return True

    def SetDirectorySubfoldersInclude(self, dirName, backupSubfolders):
        if self.backupDirs.has_key(dirName):
            self.backupDirs[dirName].SetDirectorySubfoldersInclude(backupSubfolders)
        if not self._loading:
            self.Save()

    def GetDirectoryFromBackupId(self, backupID):
        #self.CommandLog("GetDirectoryFromBackupId " + backupID)
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
        #self.CommandLog("GetTotalBackupsSize")
        backupsSize = 0
        for dirName in self.backupDirs:
            for backupRun in self.backupDirs[dirName].backupRuns:
                backupsSize += int(backupRun.backupSize)
        return backupsSize

    def ToXML(self):
        self.CommandLog("ToXML")
        dbXML = ''
##        dbXML += '<?xml version="1.0" encoding="ISO-8859-1"?>' + "\n"
        dbXML += '<?xml version="1.0" encoding="%s" ?>\n' % locale.getpreferredencoding()
        dbXML += "<backupData>\n"

        dbXML += "<backupDirectories>\n"
        for dirName in self.backupDirs:
            dbXML += self.backupDirs[dirName].ToXML()
        dbXML += "</backupDirectories>\n"

        dbXML += "<deletedBackups>\n"
        for backupID in self.deletedBackups[0-self._maxDeleted:]:
            dbXML += "  <deletedBackup>\n"
            dbXML += "    <deletedBackupId>" + backupID + "</deletedBackupId>\n"
            dbXML += "  </deletedBackup>\n"
        dbXML += "</deletedBackups>\n"

        dbXML += "</backupData>\n"
##        print 'ToXML', type(dbXML)
        return dbXML


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


InitDone = False

# We're keeping track of what directories we're backing up, what backups are
# associated with what directories
BackupDirs = None
AddDirectory = None                  # directory name
DeleteDirectory = None               # directory name
CheckDirectory = None                # directory name, return True if is in the list of directories we back up
GetBackupDirectories = None          # no input, return List of directory names
GetDirectoryInfo = None              # directory name - return
AddDirBackup = None                  # directory name, backup id, status, size, start, end
DeleteDirBackup = None               # backup id
IsDeleted = None                     # backup_id - is it in a list of deleted backup ids
SetBackupStatus = None               # directory name, backup id, status, finish time
AbortDirectoryBackup = None          # directory name - set running to false
GetLastRunInfo = None                # directory name - return last run info so backupID, backupSize, backupStatus, backupStart, backupFinish
IsBackupRunning = None               # directory name - return if an active backup is running
GetSchedule = None                   # directory name - return schedule type, time, interval, details
SetSchedule = None                   # directory name, schedule type, schedule time, schedule interval, interval details
GetLastRun = None                    # directory name - return last backup id, size, status, start, finish
GetDirBackupIds = None               # directory name - return list of all backup ids for the directory
GetBackupIds = None                  # list of all backup ids for all directories we're backing up
GetTotalBackupsSize = None           # adding up the backup runs to our best knowledge (will be a bit larger on suppliers?)
GetDirectoryFromBackupId = None      # backup id - return directory name
GetDirectorySubfoldersInclude = None # directory name - return if we back up subfolders
SetDirectorySubfoldersInclude = None # directory name, boolean (backup subfolders?)
GetBackupIdRunInfo = None            # Added by Veselin. Return RunInfo for a single BackupID
GetBackupsByDateTime = None          # return sorted by backupID list of tupples (backupID, backupDir, size, status)
GetBackupsByFolder = None            # return list of tupples (backupDir, backupRuns, totalBackupsSizeForDir, is_running, recentBackupID)   

AddRunningBackupObject = None        # backup id, running backup
GetRunningBackupObject = None        # backup id - return the backup running backup object
RemoveRunningBackupObject = None     # backup id
RemoveAllRunningBackupObjects = None # no arg, stop all running backups
HasRunningBackup = None
ShowRunningBackups = None
AbortRunningBackup = None

ToXML = None


def init():
    dhnio.Dprint(4,"backup_db.init")
    _local_backup_db = _BackupDB()
    global InitDone
    global BackupDirs
    global AddDirectory
    global DeleteDirectory
    global CheckDirectory
    global GetBackupDirectories
    global GetDirectoryInfo
    global AddDirBackup
    global DeleteDirBackup
    global IsDeleted
    global SetBackupStatus
    global AbortDirectoryBackup
    global GetLastRunInfo
    global IsBackupRunning
    global GetSchedule
    global SetSchedule
    global GetLastRun
    global GetDirBackupIds
    global GetBackupIds
    global GetTotalBackupsSize
    global GetDirectoryFromBackupId
    global GetDirectorySubfoldersInclude
    global SetDirectorySubfoldersInclude
    global GetBackupIdRunInfo
    global GetBackupsByDateTime
    global GetBackupsByFolder

    global AddRunningBackupObject
    global GetRunningBackupObject
    global RemoveRunningBackupObject
    global RemoveAllRunningBackupObjects
    global HasRunningBackup
    global ShowRunningBackups
    global AbortRunningBackup

    global ToXML

    BackupDirs = _local_backup_db.BackupDirs
    AddDirectory = _local_backup_db.AddDirectory
    DeleteDirectory = _local_backup_db.DeleteDirectory
    CheckDirectory = _local_backup_db.CheckDirectory
    GetBackupDirectories = _local_backup_db.GetBackupDirectories
    GetDirectoryInfo = _local_backup_db.GetDirectoryInfo
    AddDirBackup = _local_backup_db.AddDirBackup
    DeleteDirBackup = _local_backup_db.DeleteDirBackup
    IsDeleted = _local_backup_db.IsDeleted
    SetBackupStatus = _local_backup_db.SetBackupStatus
    AbortDirectoryBackup = _local_backup_db.AbortDirectoryBackup
    GetLastRunInfo = _local_backup_db.GetLastRunInfo
    IsBackupRunning = _local_backup_db.IsBackupRunning
    GetSchedule = _local_backup_db.GetDirSchedule
    SetSchedule = _local_backup_db.SetDirSchedule
    GetLastRun = _local_backup_db.GetDirLastBackup
    GetDirBackupIds = _local_backup_db.GetDirBackupIds
    GetBackupIds = _local_backup_db.GetBackupIds
    GetTotalBackupsSize = _local_backup_db.GetTotalBackupsSize
    GetDirectoryFromBackupId = _local_backup_db.GetDirectoryFromBackupId
    GetDirectorySubfoldersInclude = _local_backup_db.GetDirectorySubfoldersInclude
    SetDirectorySubfoldersInclude = _local_backup_db.SetDirectorySubfoldersInclude
    GetBackupIdRunInfo = _local_backup_db.GetBackupIdRunInfo
    GetBackupsByDateTime = _local_backup_db.GetBackupsByDateTime
    GetBackupsByFolder = _local_backup_db.GetBackupsByFolder

    AddRunningBackupObject = _local_backup_db.AddRunningBackupObject
    GetRunningBackupObject = _local_backup_db.GetRunningBackupObject
    RemoveRunningBackupObject = _local_backup_db.RemoveRunningBackupObject
    RemoveAllRunningBackupObjects = _local_backup_db.RemoveAllRunningBackupObjects
    HasRunningBackup = _local_backup_db.HasRunningBackup
    ShowRunningBackups = _local_backup_db.ShowRunningBackups
    AbortRunningBackup = _local_backup_db.AbortRunningBackup

    ToXML = _local_backup_db.ToXML
    
    _local_backup_db.Load()
    
    _local_backup_db.AskSizeForAllDirs()

    #init state
    InitDone = True


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
