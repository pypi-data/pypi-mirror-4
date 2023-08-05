#!/usr/bin/python
#io_throttle.py
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2012
#    All rights reserved.
#
#    When reconstructing a backup we don't want to take over everything
#    and make DHN unresponsive by requesting 1000's of files at once
#    and make it so no other packets can go out,
#    this just tries to limit how much we are sending out or receiving at any time
#    so that we still have control.
#    Before requesting another file or sending another one out
#    I check to see how much stuff I have waiting.  


import os
import sys
import time


try:
    from twisted.internet import reactor
except:
    sys.exit('Error initializing twisted.internet.reactor in io_throttle.py')


import lib.transport_control as transport_control
import lib.dhnio as dhnio
import lib.settings as settings
import lib.dhnpacket as dhnpacket
import lib.commands as commands
import lib.misc as misc
import lib.tmpfile as tmpfile
import lib.nameurl as nameurl


import contacts_status

#------------------------------------------------------------------------------ 


class FileToRequest:
    def __init__(self, callOnReceived, creatorID, packetID, ownerID, remoteID):
        self.callOnReceived = []
        self.callOnReceived.append(callOnReceived)
        self.creatorID = creatorID
        self.packetID = packetID
        self.ownerID = ownerID
        self.remoteID = remoteID
        self.backupID = packetID[0:packetID.find("-")]
        self.requestTime = None
        self.fileReceivedTime = None


class FileToSend:
    def __init__(self, fileName, packetID, remoteID, ownerID, callOnAck=None, callOnFail=None):
        self.fileName = fileName
        try:
            self.fileSize = os.path.getsize(os.path.abspath(fileName))
        except:
            dhnio.DprintException()
            self.fileSize = 0
        self.timeout = int(self.fileSize / settings.SendingSpeedLimit())
        self.packetID = packetID
        self.remoteID = remoteID
        self.ownerID = ownerID
        self.callOnAck = callOnAck
        self.callOnFail = callOnFail
        self.sendTime = None
        self.ackTime = None


#TODO I'm not removing items from the dict's at the moment
class SupplierQueue:
    def __init__(self, supplierIdentity, creatorID):
        self.creatorID = creatorID
        self.remoteID = supplierIdentity
        self.remoteName = nameurl.GetName(self.remoteID)

        # all sends we'll hold on to, only several will be active, 
        # but will hold onto the next ones to be sent
        # self.fileSendQueueMaxLength = 32
        # active files 
        self.fileSendMaxLength = 1 # 1 mean sending files one by one! 
        # an array of packetId, preserving first in first out, 
        # of which the first maxLength are the "active" sends      
        self.fileSendQueue = []
        # dictionary of FileToSend's using packetId as index, 
        # hold onto stuff sent and acked for some period as a history?         
        self.fileSendDict = {}          

        # all requests we'll hold on to, 
        # only several will be active, but will hold onto the next ones to be sent
        self.fileRequestQueueMaxLength = 6
        # active requests 
        self.fileRequestMaxLength = 1 # do requests one by one   
        # an arry of PacketIDs, preserving first in first out
        self.fileRequestQueue = []      
        # FileToRequest's, indexed by PacketIDs
        self.fileRequestDict = {}       

        # in theory transport_control should handle resending, 
        # but in case it doesn't ...
        self.baseTimeout = settings.SendTimeOut()
        # 30 minutes 
        self.maxTimeout = 1800
        # when do we decide a request has timed out 
        # and what is the backoff for this supplier          
        self.timeout = self.baseTimeout 

        self.dprintAdjust = 0
        self.shutdown = False

        self.ackedCount = 0
        self.failedCount = 0
        
        self.sendFailedPacketIDs = []
        
        self.sendTask = None
        self.sendTaskDelay = 0.1
        self.requestTask = None
        self.requestTaskDelay = 0.1


#    def OkToQueueRequest(self):
#        return len(self.fileRequestQueue) < self.fileRequestQueueMaxLength


#    def OkToQueueSend(self):
#        return len(self.fileSendQueue) < self.fileSendQueueMaxLength


    def RemoveSupplierWork(self): 
        # in the case that we're doing work with a supplier who has just been replaced ...
        # Need to remove the register interests
        # our dosend is using acks?
        self.shutdown = True
        #newpacket = dhnpacket.dhnpacket(commands.Data(), fileToSend.ownerID, self.creatorID, fileToSend.packetID, Payload, fileToSend.remoteID)
        for i in range(min(self.fileSendMaxLength, len(self.fileSendQueue))):
            fileToSend = self.fileSendDict[self.fileSendQueue[i]]
            transport_control.RemoveSupplierRequestFromSendQueue(fileToSend.packetID, fileToSend.remoteID, commands.Data())
            transport_control.RemoveInterest(fileToSend.remoteID, fileToSend.packetID)
        for i in range(min(self.fileRequestMaxLength, len(self.fileRequestQueue))):
            fileToRequest = self.fileRequestDict[self.fileRequestQueue[i]]
            transport_control.RemoveSupplierRequestFromSendQueue(fileToRequest.packetID, fileToRequest.remoteID, commands.Retrieve())
            transport_control.RemoveInterest(fileToRequest.remoteID, fileToRequest.packetID)


    def SupplierSendFile(self, fileName, packetID, ownerID, callOnAck=None, callOnFail=None):
        if self.shutdown: 
            dhnio.Dprint(8, "io_throttle.SupplierSendFile finishing to %s, shutdown is True" % self.remoteName)
            return        
        if contacts_status.isOffline(self.remoteID):
            dhnio.Dprint(8, "io_throttle.SupplierSendFile %s is offline, so packet %s is failed" % (self.remoteName, packetID))
            if callOnFail is not None:
                reactor.callLater(0, callOnFail, self.remoteID, packetID, 'offline')
            return
        if packetID in self.fileSendQueue:
            dhnio.Dprint(4, "io_throttle.SupplierSendFile WARNING packet %s already in the queue for %s" % (packetID, self.remoteName))
            if callOnFail is not None:
                reactor.callLater(0, callOnFail, self.remoteID, packetID, 'in queue')
            return
        self.fileSendQueue.append(packetID)
        self.fileSendDict[packetID] = FileToSend(
            fileName, 
            packetID, 
            self.remoteID, 
            ownerID, 
            callOnAck,
            callOnFail,)
        dhnio.Dprint(8, "io_throttle.SupplierSendFile %s to %s, queue length is %s" % (packetID, self.remoteName, len(self.fileSendQueue)))
        # reactor.callLater(0, self.DoSend)
        self.DoSend()
            
            
    def RunSend(self):
        #dhnio.Dprint(6, 'io_throttle.RunSend')
        packetsFialed = []
        packetsToRemove = []
        packetsSent = 0
        # let's check all packets in the queue        
        for i in range(len(self.fileSendQueue)):
            packetID = self.fileSendQueue[i]
            fileToSend = self.fileSendDict[packetID]
            # we got notify that this packet was failed to send
            if packetID in self.sendFailedPacketIDs:
                self.sendFailedPacketIDs.remove(packetID)
                packetsFialed.append((packetID, 'failed'))
                continue
            # we already sent the file
            if fileToSend.sendTime is not None:
                packetsSent += 1
                # and we got ack
                if fileToSend.ackTime is not None:
                    deltaTime = fileToSend.ackTime - fileToSend.sendTime
                    # so remove it from queue
                    packetsToRemove.append(packetID)
                # if we do not get an ack ...    
                else:
                    # ... we do not want to wait to long
                    deltaTime = time.time() - fileToSend.sendTime
                    if deltaTime > fileToSend.timeout:
                        # so this packet is failed because no response on it 
                        packetsFialed.append((packetID, 'timeout'))
                # we sent this packet already - check next one
                continue
            # the data file to send no longer exists - it is failed situation
            if not os.path.exists(fileToSend.fileName):
                dhnio.Dprint(4, "io_throttle.RunSend WARNING file %s not exist" % (fileToSend.fileName))
                packetsFialed.append((packetID, 'not exist'))
                continue
            # do not send too many packets, need to wait for ack
            # hold other packets in the queue and may be send next time
            if packetsSent > self.fileSendMaxLength:
                # if we sending big file - we want to wait
                # other packets must go without waiting in the queue
                # 10K seems fine, because we need to filter only Data and Parity packets here
                try:
                    if os.path.getsize(fileToSend.fileName) > 1024 * 10:
                        continue
                except:
                    dhnio.DprintException()
                    continue
            # prepare the packet
            Payload = str(dhnio.ReadBinaryFile(fileToSend.fileName))
            newpacket = dhnpacket.dhnpacket(
                commands.Data(), 
                fileToSend.ownerID, 
                self.creatorID, 
                fileToSend.packetID, 
                Payload, 
                fileToSend.remoteID)
            # outbox will not resend, because no ACK, just data, 
            # need to handle resends on own
            transport_control.outboxNoAck(newpacket)  
            transport_control.RegisterInterest(
                self.FileSendAck, 
                fileToSend.remoteID, 
                fileToSend.packetID)
            # mark file as been sent
            fileToSend.sendTime = time.time()
            packetsSent += 1
        # process failed packets
        for packetID, why in packetsFialed:
            self.FileSendFailed(self.fileSendDict[packetID].remoteID, packetID, why)
            packetsToRemove.append(packetID)
        # remove finished packets    
        for packetID in packetsToRemove:
            self.fileSendQueue.remove(packetID)
            del self.fileSendDict[packetID]
        # if sending queue is empty - remove all records about packets failed to send
        if len(self.fileSendQueue) == 0:
            del self.sendFailedPacketIDs[:]
        # remember results
        result = max(len(packetsToRemove), packetsSent)
        # erase temp lists    
        del packetsFialed
        del packetsToRemove
        return result
        

    def SendingTask(self):
        #dhnio.Dprint(6, 'io_throttle.SendingTask')
        if self.RunSend() > 0:
            self.sendTaskDelay = 0.2
        else:
            if self.sendTaskDelay < 8.0:
                self.sendTaskDelay *= 2.0
        # attenuation
        self.sendTask = reactor.callLater(self.sendTaskDelay, self.SendingTask)
        
    
    def DoSend(self):
        #dhnio.Dprint(6, 'io_throttle.DoSend')
        if self.sendTask is None:
            self.SendingTask()
        else:
            if self.sendTaskDelay > 1.0:
                self.sendTask.cancel()
                self.sendTask = None
                self.SendingTask()
            

    def FileSendAck(self, packet):    
        if self.shutdown: 
            dhnio.Dprint(8, "io_throttle.FileSendAck finishing to %s, shutdown is True" % self.remoteName)
            return
        self.ackedCount += 1
        self.timeout = self.baseTimeout
        if packet.PacketID not in self.fileSendQueue:
            dhnio.Dprint(4, "io_throttle.FileSendAck WARNING packet %s not in sending queue for %s" % (packet.PacketID, self.remoteName))
            return
        if packet.PacketID not in self.fileSendDict.keys():
            dhnio.Dprint(4, "io_throttle.FileSendAck WARNING packet %s not in sending dict for %s" % (packet.PacketID, self.remoteName))
            return
        self.fileSendDict[packet.PacketID].ackTime = time.time()
        if self.fileSendDict[packet.PacketID].callOnAck:
            reactor.callLater(0, self.fileSendDict[packet.PacketID].callOnAck, packet, packet.OwnerID, packet.PacketID)
        # reactor.callLater(0, self.DoSend)
        self.DoSend()

        
    def FileSendFailed(self, RemoteID, PacketID, why):
        if self.shutdown: 
            dhnio.Dprint(8, "io_throttle.FileSendFailed finishing to %s, shutdown is True" % self.remoteName)
            return
        self.failedCount += 1
        if PacketID not in self.fileSendDict.keys():
            dhnio.Dprint(4, "io_throttle.FileSendFailed WARNING packet %s not in send dict" % PacketID)
            return
        fileToSend = self.fileSendDict[PacketID]
        transport_control.RemoveSupplierRequestFromSendQueue(fileToSend.packetID, fileToSend.remoteID, commands.Data())
        transport_control.RemoveInterest(fileToSend.remoteID, fileToSend.packetID)
        if why == 'timeout':
            contacts_status.PacketSendingTimeout(RemoteID, PacketID)
        if fileToSend.callOnFail:
            reactor.callLater(0, fileToSend.callOnFail, RemoteID, PacketID, why)
        # reactor.callLater(0, self.DoSend)
        self.DoSend()


    def SupplierRequestFile(self, callOnReceived, creatorID, packetID, ownerID):
        if self.shutdown: 
            dhnio.Dprint(8, "io_throttle.SupplierRequestFile finishing to %s, shutdown is True" % self.remoteName)
            reactor.callLater(0, callOnReceived, None)
            return
        if packetID in self.fileRequestQueue:
            dhnio.Dprint(4, "io_throttle.SupplierRequestFile WARNING packet %s already in the queue for %s" % (packetID, self.remoteName))
            reactor.callLater(0, callOnReceived, None)
            return
        self.fileRequestQueue.append(packetID)
        self.fileRequestDict[packetID] = FileToRequest(
            callOnReceived, creatorID, packetID, ownerID, self.remoteID)
        dhnio.Dprint(8, "io_throttle.SupplierRequestFile for %s from %s, queue length is %d" % (packetID, self.remoteName, len(self.fileRequestQueue)))
        # reactor.callLater(0, self.DoRequest)
        self.DoRequest()


    def RunRequest(self):
        #dhnio.Dprint(6, 'io_throttle.RunRequest')
        packetsToRemove = []
        for i in range(0,min(self.fileRequestMaxLength, len(self.fileRequestQueue))):
            packetID = self.fileRequestQueue[i]
            currentTime = time.time()
            if self.fileRequestDict[packetID].requestTime is not None:
                if self.fileRequestDict[packetID].fileReceivedTime is None:
                    if currentTime - self.fileRequestDict[packetID].requestTime > self.timeout:
                        self.fileRequestDict[packetID].requestTime = None
                        self.timeout = min(2 * self.timeout, self.maxTimeout)
                else:
                    packetsToRemove.append(packetID)
            if self.fileRequestDict[packetID].requestTime is None:
                # if not os.path.exists(os.path.join(tmpfile.subdir('data-par'), packetID)): 
                if not os.path.exists(os.path.join(settings.getLocalBackupsDir(), packetID)): 
                    fileRequest = self.fileRequestDict[packetID]
                    dhnio.Dprint(8, "io_throttle.RunRequest for packetID " + fileRequest.packetID)
                    transport_control.RegisterInterest(
                        self.DataReceived, 
                        fileRequest.creatorID, 
                        fileRequest.packetID)
                    newpacket = dhnpacket.dhnpacket(
                        commands.Retrieve(), 
                        fileRequest.ownerID, 
                        fileRequest.creatorID, 
                        fileRequest.packetID, 
                        "", 
                        fileRequest.remoteID)
                    transport_control.outboxNoAck(newpacket)  
                    fileRequest.requestTime = time.time()
                else:
                    # we have the data file, no need to request it
                    packetsToRemove.append(packetID)
        # remember requests results
        result = len(packetsToRemove)
        # remove finished requests
        if len(packetsToRemove) > 0:
            for packetID in packetsToRemove:
                self.fileRequestQueue.remove(packetID)
        del packetsToRemove
        return result


    def RequestTask(self):
        #dhnio.Dprint(6, 'io_throttle.RequestTask')
        if self.shutdown:
            return
        if self.RunRequest() > 0:
            self.requestTaskDelay = 0.1
        else:
            if self.requestTaskDelay < 8.0:
                self.requestTaskDelay *= 2.0
        # attenuation
        self.requestTask = reactor.callLater(self.requestTaskDelay, self.RequestTask)
        
    
    def DoRequest(self):
        #dhnio.Dprint(6, 'io_throttle.DoRequest')
        if self.requestTask is None:
            self.RequestTask()
        else:
            if self.requestTaskDelay > 1.0:
                self.requestTask.cancel()
                self.requestTask = None
                self.RequestTask()


    def DataReceived(self, packet):   
        # we requested some data from a supplier, just received it
        if self.shutdown: 
            # if we're closing down this queue (supplier replaced, don't any anything new)
            return
        self.timeout = self.baseTimeout
        dhnio.Dprint(10, "io_throttle.DataReceived " + packet.PacketID)
        if packet.PacketID in self.fileRequestQueue:
            self.fileRequestQueue.remove(packet.PacketID)
        if self.fileRequestDict.has_key(packet.PacketID):
            self.fileRequestDict[packet.PacketID].fileReceivedTime = time.time()
            for callBack in self.fileRequestDict[packet.PacketID].callOnReceived:
                callBack(packet)
        if self.fileRequestDict.has_key(packet.PacketID):
            del self.fileRequestDict[packet.PacketID]
        # reactor.callLater(0, self.DoRequest)
        self.DoRequest()


#    def CheckOk(self):
#        if self.shutdown: 
#            # if we're closing down this queue 
#            # (supplier replaced, don't any anything new)
#            return
#        currentTime = time.time()
#        # do we need to do anything to check the data send queue since the DoSend is using the transport_control.outbox
#        # that keeps trying until it gets an ACK, so at this time ... do nothing for the send queue?
#        # running into trouble that the outbox that should retry until an ACK doesn't seem to be working right
#        if True: # turn this off later if problem appears to be solved
#            doSend = False
#            for i in range(min(self.fileSendMaxLength, len(self.fileSendQueue))):
#                packetID = self.fileSendQueue[i]
#                if self.fileSendDict[packetID].sendTime is None:
#                    doSend = True
#                    break
#                if self.fileSendDict[packetID].ackTime is None:
#                    if (currentTime - self.fileSendDict[packetID].sendTime) > self.baseTimeout:
#                        #self.fileSendDict[packetID].sendTime = None
#                        #self.timeout = min(2 * self.timeout,self.maxTimeout)
#                        doSend = True
#                        break
#        if doSend:
#            # reactor.callLater(0, self.DoSend)
#            self.DoSend()
#
#        # now for the request queue...
#        #dhnio.Dprint(11, "io_throttle.SupplierQueue.CheckOk for supplier " + self.supplierIdentity + " at " + str(currentTime) + ", timeout=" + str(self.timeout))
#        doRequest = False
#        for i in range(min(self.fileRequestMaxLength, len(self.fileRequestQueue))):
#            packetID = self.fileRequestQueue[i]
#            #dhnio.Dprint(12, "io_throttle.SupplierQueue.CheckOk request time for packet " + packetID + ", requested at " + str(self.fileRequestDict[packetID].requestTime))
#            if self.fileRequestDict[packetID].requestTime is None:
#                #dhnio.Dprint(13, "io_throttle.SupplierQueue.CheckOk found a queued item that hadn't been sent")
#                doRequest = True
#                break
#            elif self.fileRequestDict[packetID].fileReceivedTime is None:
#                if currentTime - self.fileRequestDict[packetID].requestTime > self.timeout:
#                    #dhnio.Dprint(11, "io_throttle.SupplierQueue.CheckOk found a queued item that timed out ")
#                    # this will mart file for request one more time
#                    # TODO need to keep eye on this
#                    self.fileRequestDict[packetID].requestTime = None
#                    self.timeout = min(2 * self.timeout, self.maxTimeout)
#                    doRequest = True
#                    break
#        if doRequest:
#            # reactor.callLater(0, self.DoRequest)
#            self.DoRequest()


    def DeleteBackupRequests(self, backupName):
        if self.shutdown: 
            # if we're closing down this queue 
            # (supplier replaced, don't any anything new)
            return
        packetsToRemove = []
        for packetID in self.fileSendQueue:
            if packetID.find(backupName) == 0:
                self.FileSendFailed(self.fileSendDict[packetID].remoteID, packetID, 'delete request')
                packetsToRemove.append(packetID)
                dhnio.Dprint(8, 'io_throttle.DeleteBackupRequests %s from send queue' % packetID)
        for packetID in packetsToRemove:
            self.fileSendQueue.remove(packetID)
            del self.fileSendDict[packetID]
        packetsToRemove = []
        for packetID in self.fileRequestQueue:
            if packetID.find(backupName) == 0:
                packetsToRemove.append(packetID)
                dhnio.Dprint(8, 'io_throttle.DeleteBackupRequests %s from request queue' % packetID)
        for packetID in packetsToRemove:
            self.fileRequestQueue.remove(packetID)
            del self.fileRequestDict[packetID]
        if len(self.fileRequestQueue) > 0:
            reactor.callLater(0, self.DoRequest)
        if len(self.fileSendQueue) > 0:
            reactor.callLater(0, self.DoSend)
            #self.DoSend()


    def OutboxStatus(self, workitem, proto, host, status, error, message):
        packetID = workitem.packetid
        if status == 'failed' and packetID in self.fileSendQueue:
            self.sendFailedPacketIDs.append(packetID)
            # reactor.callLater(0, self.DoSend)
            self.DoSend()
            
    

# all of the backup rebuilds will run their data requests through this 
# so it gets throttled, also to reduce duplicate requests
class IOThrottle:
    def __init__(self):
        self.creatorID = misc.getLocalID()
        self.supplierQueues = {} #
        self.dprintAdjust = 0
        #reactor.callLater(60, self.CheckOk) # 1 minute


#    def CheckOk(self):
#        #if settings.getDoBackupMonitor() == "Y":
#        for supplierIdentity in self.supplierQueues.keys():
#            self.supplierQueues[supplierIdentity].CheckOk()
#        reactor.callLater(60, self.CheckOk) 


    def DeleteSuppliers(self, supplierIdentities):
        for supplierIdentity in supplierIdentities:
            if self.supplierQueues.has_key(supplierIdentity):
                self.supplierQueues[supplierIdentity].RemoveSupplierWork()
                del self.supplierQueues[supplierIdentity]


    def DeleteBackupRequests(self, backupName):
        #if settings.getDoBackupMonitor() == "Y":
        for supplierIdentity in self.supplierQueues.keys():
            self.supplierQueues[supplierIdentity].DeleteBackupRequests(backupName)


    def QueueSendFile(self, fileName, packetID, remoteID, ownerID, callOnAck=None, callOnFail=None):
        #dhnio.Dprint(8, "io_throttle.QueueSendFile %s to %s" % (packetID, nameurl.GetName(remoteID)))
        if not os.path.exists(fileName):
            dhnio.Dprint(2, "io_throttle.QueueSendFile ERROR %s not exist" % fileName)
            if callOnFail is not None:
                reactor.callLater(.01, callOnFail, remoteID, packetID, 'not exist')
            return
        if remoteID not in self.supplierQueues.keys():
            self.supplierQueues[remoteID] = SupplierQueue(remoteID, self.creatorID)
            dhnio.Dprint(6, "io_throttle.QueueSendFile made a new queue for %s" % nameurl.GetName(remoteID))
        self.supplierQueues[remoteID].SupplierSendFile(
            fileName, packetID, ownerID, callOnAck, callOnFail,)
            

    def QueueRequestFile(self, callOnReceived, creatorID, packetID, ownerID, remoteID):
        # make sure that we don't actually already have the file
        filename = os.path.join(settings.getLocalBackupsDir(), packetID)
        if os.path.exists(filename):
            dhnio.Dprint(4, "io_throttle.QueueRequestFile WARNING %s already exist " % filename)
            reactor.callLater(0, callOnReceived, None)
            return
        if remoteID not in self.supplierQueues.keys():
            # made a new queue for this man
            self.supplierQueues[remoteID] = SupplierQueue(remoteID, self.creatorID)
            dhnio.Dprint(6, "io_throttle.QueueRequestFile made a new queue for %s" % nameurl.GetName(remoteID))
        # if packetID not in self.supplierQueues[remoteID].fileRequestQueue and not os.path.exists(os.path.join(tmpfile.subdir('data-par'), packetID)):
        #dhnio.Dprint(8, "io_throttle.QueueRequestFile asking for %s from %s" % (packetID, nameurl.GetName(remoteID)))
        self.supplierQueues[remoteID].SupplierRequestFile(callOnReceived, creatorID, packetID, ownerID)


    def InboxStatus(self, newpacket, status, proto, host, error, message):
        pass
        
    
    def OutboxStatus(self, workitem, proto, host, status, error, message):
#        if settings.getDoBackupMonitor() == "Y":
        for supplierIdentity in self.supplierQueues.keys():
            self.supplierQueues[supplierIdentity].OutboxStatus(workitem, proto, host, status, error, message)

#------------------------------------------------------------------------------ 

QueueSendFile = None
QueueRequestFile = None
#OkToQueueRequest = None
#OkToQueueSend = None
DeleteBackupRequests = None
DeleteSuppliers = None
InboxStatus = None
OutboxStatus = None

def init():
    dhnio.Dprint(4,"io_throttle.init")
    global QueueSendFile
    global QueueRequestFile
#    global OkToQueueRequest
#    global OkToQueueSend
    global DeleteBackupRequests
    global DeleteSuppliers
    global InboxStatus
    global OutboxStatus
    _throttle = IOThrottle()
    QueueSendFile = _throttle.QueueSendFile
    #QueueSendFile = _debugSending
    QueueRequestFile = _throttle.QueueRequestFile
#    OkToQueueRequest = _throttle.OkToQueueRequest
#    OkToQueueSend = _throttle.OkToQueueSend
    DeleteBackupRequests = _throttle.DeleteBackupRequests
    DeleteSuppliers = _throttle.DeleteSuppliers
    InboxStatus = _throttle.InboxStatus
    OutboxStatus = _throttle.OutboxStatus
    #transport_control.AddInboxPacketStatusFunc(InboxStatus)
    transport_control.AddOutboxPacketStatusFunc(OutboxStatus)
    
#------------------------------------------------------------------------------ 

def _debugSending(fileName, packetID, remoteID, ownerID, callOnAck=None, callOnFail=None):
#    import random
#    if random.randint(0, 3) > 1:
#        reactor.callLater(1, callOnAck, None, remoteID, packetID)
#    else:
    dhnio.Dprint(6, 'io_throttle._debugSending ' + packetID)
    reactor.callLater(1, callOnFail, remoteID, packetID, 'failed')
        
    
    
    
