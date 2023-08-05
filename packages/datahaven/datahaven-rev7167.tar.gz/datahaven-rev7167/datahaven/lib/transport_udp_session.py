#!/usr/bin/python
#transport_udp_session.py
#
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2012
#    Use of this software constitutes acceptance of the Terms of Use
#      http://datahaven.net/terms_of_use.html
#    All rights reserved.
#
#


import os
import time
import struct
import cStringIO
import random


from twisted.internet import reactor
from twisted.internet.task import LoopingCall 


import dhnio
import settings
import misc
import identity
import identitycache
import tmpfile 
import nameurl

import automat
import automats

#------------------------------------------------------------------------------ 

CODES = {'p:':  'PING',
         'g:':  'GREETING',
         'd:':  'DATA',
         'r:':  'REPORT',
         'a:':  'ALIVE',}

COMMANDS = {'PING':         'p:',
            'GREETING':     'g:',
            'DATA':         'd:',
            'REPORT':       'r:',
            'ALIVE':        'a:',}

BLOCK_SIZE_LEVELS = {   #0: 508,
                        0: 1460,
                        1: 2048,
                        2: 3072,
                        3: 4096,
                        4: 5120,
                        5: 6144,
                        6: 7168,
                        7: 8124,
                        }
MAX_BLOCK_SIZE_LEVEL = len(BLOCK_SIZE_LEVELS) - 1

#BLOCK_SIZE = 4096
TIME_OUT = 20
BLOCK_RETRIES = 5
MAX_WINDOW_SIZE = 32
MIN_WINDOW_SIZE = 1

_ParentObject = None
_SessionsDict = {}
_IdToAddress = {}
_AddressToId = {}

_SendStatusCallback = None
_ReceiveStatusCallback = None
_SendControlFunc = None
_ReceiveControlFunc = None
_RegisterTransferFunc = None
_UnRegisterTransferFunc = None

_Timer1sec = None
_Timer10sec = None
_Timer30sec = None

_SendingDelay = 0.01
_SendingTask = None

_OutboxQueueDelay = 0.01
_OutboxQueueTask = None

#------------------------------------------------------------------------------ 

def init(parent):
    global _ParentObject
    dhnio.Dprint(4, 'transport_udp_session.init')
    _ParentObject = parent
    reactor.callLater(0, process_outbox_queue)
    reactor.callLater(1, process_sending)
    StartTimers()
   
def shutdown():
    dhnio.Dprint(4, 'transport_udp_session.shutdown')
    StopTimers()
    
   
def A(address, event=None, arg=None):
    global _SessionsDict
    s = open_session(address, arg)
    if event is not None:
        s.automat(event, arg)
    return s
      

def open_session(address, arg):
    global _SessionsDict
    if _SessionsDict.has_key(address):
        return _SessionsDict[address]
    dhnio.Dprint(6, 'transport_udp_session.open_session making new entry for [%s], arg=%s' % (str(address), str(arg)))
    idurl = None
    idname = 'unknown'
    if isinstance(arg, str) and arg.startswith('http://'):
        idurl = arg
        idname = nameurl.GetName(idurl)
    if idurl is None:
        idurl_remote = identitycache.GetIDURLByIPPort(address[0], address[1])
        local_address = identitycache.RemapContactAddress(address)
        idurl_local = identitycache.GetIDURLByIPPort(local_address[0], local_address[1])
        if idurl_local:
            idurl = idurl_local
            dhnio.Dprint(6, 'transport_udp_session.open_session found idurl when remap local IP : ' + idurl)
        else:
            if idurl_remote:
                idurl = idurl_remote 
                dhnio.Dprint(6, 'transport_udp_session.open_session found idurl from IP and PORT : ' + idurl)
        idname = nameurl.GetName(idurl)
    name = 'udp_%s_(%s:%s)' % (idname, address[0], address[1])
    s = TransportUDPSession(address, name, 'AT_STARTUP', 12)
    _SessionsDict[address] = s
    s.event('init', idurl)
    return s
    
#------------------------------------------------------------------------------ 
    
class OutboxFile():
    def __init__(self, peer, remote_idurl, file_id, filename):
        global _RegisterTransferFunc
        self.peer = peer
        self.remote_idurl = remote_idurl
        self.file_id = file_id
        self.filename = filename
        try:
            self.size = os.path.getsize(self.filename)
        except:
            self.size = -1
        self.block_id = -1
        self.num_blocks = 0
        self.blocks = {} 
        self.bytes_sent = 0
        self.failed_blocks = {}
        self.has_failed_blocks = False
        self.transfer_id = None
        if _RegisterTransferFunc is not None:
            self.transfer_id = _RegisterTransferFunc('send', self.peer.remote_address, self.get_bytes_sent, self.filename, self.size)
        # dhnio.Dprint(6, 'transport_udp_session.OutboxFile [%d] to %s' % (self.file_id, nameurl.GetName(self.remote_idurl)))

    def close(self):
        global _UnRegisterTransferFunc
        if _UnRegisterTransferFunc is not None and self.transfer_id is not None:
            _UnRegisterTransferFunc(self.transfer_id)
        # dhnio.Dprint(6, 'transport_udp_session.OutboxFile close [%d] to %s (%s)' % (self.file_id, nameurl.GetName(self.remote_idurl), str(self.peer)))

    def get_bytes_sent(self):
        return self.bytes_sent 

    def report_block(self, block_id):
        if not self.blocks.has_key(block_id):
            # dhnio.Dprint(2, 'transport_udp_session.report_block WARNING unknown block_id in REPORT packet received from %s: [%d]' % (self.remote_address, block_id))
            return
        self.bytes_sent += len(self.blocks[block_id])
        del self.blocks[block_id]

    def send(self):
        do_send = False
        while len(self.peer.sliding_window) < self.peer.sliding_window_size and self.block_id < self.num_blocks and self.block_id >= 0:
            if not self.send_block(self.block_id):
                break
            self.peer.sliding_window[(self.file_id, self.block_id)] = time.time()
            self.block_id += 1
        return do_send
    
    def send_block(self, block_id):
        global _SendControlFunc
        data = self.blocks[block_id]
        if _SendControlFunc is not None:
            more_bytes = _SendControlFunc(self.peer.last_bytes_sent, len(data))
            if more_bytes < len(data):
                return False
        self.peer.last_bytes_sent = len(data)
        datagram = COMMANDS['DATA']
        datagram += struct.pack('i', self.file_id)
        datagram += struct.pack('i', block_id)
        datagram += struct.pack('i', self.num_blocks)
        datagram += struct.pack('i', len(data))
        datagram += data
        return self.peer.sendDatagram(datagram)

    def mark_failed_block(self, block_id):
        if not self.failed_blocks.has_key(block_id):
            self.failed_blocks[block_id] = 0
        self.failed_blocks[block_id] += 1
        if self.failed_blocks[block_id] >= BLOCK_RETRIES:
            self.has_failed_blocks = True
            # dhnio.Dprint(8, 'transport_udp_session.markFailedBlock (%d,%d) is failed to send' % (self.current_file_id, block_id))
            return True
        return False
    
    def read_blocks(self):
        fin = open(self.filename, 'rb')
        block_id = 0
        while True:
            block_data = fin.read(BLOCK_SIZE_LEVELS[self.peer.block_size_level])
            if block_data == '':
                break
            self.blocks[block_id] = block_data
            block_id += 1  
        fin.close()
        self.num_blocks = block_id
        self.block_id = 0     

#------------------------------------------------------------------------------ 


class InboxFile():
    def __init__(self, peer, file_id, num_blocks):
        global _RegisterTransferFunc
        self.fd, self.filename = tmpfile.make("udp-in")
        self.peer = peer
        self.file_id = file_id
        self.num_blocks = num_blocks
        self.blocks = {}
        self.bytes_received = 0
        self.transfer_id = None
        if _RegisterTransferFunc is not None:
            self.transfer_id = _RegisterTransferFunc('receive', self.peer.remote_address, self.get_bytes_received, self.filename, -1)
        # dhnio.Dprint(6, 'transport_udp_session.InboxFile {%s} [%d] from %s' % (self.transfer_id, self.file_id, str(self.peer.remote_address)))

    def close(self):
        global _UnRegisterTransferFunc
        if _UnRegisterTransferFunc is not None and self.transfer_id is not None:
            _UnRegisterTransferFunc(self.transfer_id)
        # dhnio.Dprint(6, 'transport_udp_session.InboxFile.close {%s} [%d] from %s' % (self.transfer_id, self.file_id, str(self.peer.remote_address)))

    def get_bytes_received(self):
        return self.bytes_received

    def input_block(self, block_id, block_data):
        self.blocks[block_id] = block_data
        self.bytes_received += len(block_data) 
    
    def build(self):
        for block_id in range(len(self.blocks)):
            os.write(self.fd, self.blocks[block_id])
        os.close(self.fd)
        # dhnio.Dprint(10, 'transport_udp_server.InboxFile.build [%s] file_id=%d, blocks=%d' % (
        #     os.path.basename(filename), file_id, len(self.incommingFiles[file_id])))
    
#------------------------------------------------------------------------------ 

class TransportUDPSession(automat.Automat):
    timers = {#'timer-1min':     (60,    ['CONNECTED', 'SENDING']),
              #'timer-30sec':    (30,    ['GREETING', 'PING', 'DISCONNECTED']),
              #'timer-1sec':     (1,     ['PING', 'GREETING', 'CONNECTED']),
              #'timer-01sec':    (0.02,   ['SENDING',])
              }
    def __init__(self, address, name, state, debug_level):
        global _ParentObject
        self.remote_address = address
        self.remote_idurl = None
        self.parent = _ParentObject
        self.client = _ParentObject.client
        self.last_alive_packet_time = 0
        self.incommingFiles = {}
        self.outgoingFiles = {}
        self.maxOutgoingFiles = 4
        self.receivedFiles = {}
        self.outbox_queue = []
        self.tries = 0
        self.sliding_window = {}
        self.sliding_window_size = MIN_WINDOW_SIZE
        self.last_bytes_sent = 0
        self.failedBlocks = {}
        self.hasFailedBlocks = False
        self.block_size_level = 0
        automat.Automat.__init__(self, name, state, debug_level)
        
    def A(self, event, arg):
        #---CONNECTED---
        if self.state == 'CONNECTED':
            if event == 'datagram-received':
                self.doReceiveData(arg)
            elif event == 'timer-30sec' and self.isAlive():
                self.doAlive()
            elif event == 'timer-30sec' and not self.isAlive():
                self.state = 'DISCONNECTED'
            elif event == 'shutdown':
                self.doDestroyMe()
                self.state = 'CLOSED'
        #---AT_STARTUP---
        elif self.state == 'AT_STARTUP':
            if event == 'init':
                self.doSaveIDURL(arg)
                self.doRequestRemoteID()
                self.state = 'REMOTE_ID'
        #---REMOTE_ID---
        elif self.state == 'REMOTE_ID':
            if event == 'remote-id-received' and not self.isIPPortChanged():
                self.doPing()
                self.state = 'PING'
            elif event == 'remote-id-received' and self.isIPPortChanged():
                self.parent.A('ip-port-changed', self.remote_idurl)
                self.doDestroyMe()
                self.state = 'CLOSED'
            elif event == 'remote-id-failed':
                self.state = 'DISCONNECTED'
            elif event == 'datagram-received':
                self.doReceiveData(arg)
            elif event == 'shutdown':                
                self.doDestroyMe()
                self.state = 'CLOSED'
        #---PING---
        elif self.state == 'PING':
            if event == 'datagram-received' and self.isPingOrGreeting(arg):
                self.doGreeting()
                self.state = 'GREETING'
            elif event == 'datagram-received' and not self.isPingOrGreeting(arg):
                self.doReceiveData(arg)
            elif event == 'timer-1sec':
                self.doPing()
            elif event == 'timer-30sec':
                self.state = 'DISCONNECTED'
            elif event == 'shutdown':
                self.doDestroyMe()
                self.state = 'CLOSED'
        #---GREETING---
        elif self.state == 'GREETING':
            if event == 'datagram-received' and self.isGreetingOrAlive(arg):
                self.doAlive()
                self.state = 'CONNECTED'
            elif event == 'datagram-received' and not self.isGreetingOrAlive(arg):
                self.doReceiveData(arg)
            elif event == 'timer-1sec':
                self.doGreeting()
            elif  event == 'timer-30sec':
                self.state = 'DISCONNECTED'
            elif event == 'shutdown':
                self.doDestroyMe()
                self.state = 'CLOSED'
        #---DISCONNECTED---
        elif self.state == 'DISCONNECTED':
            if event == 'timer-10sec':
                self.doRequestRemoteID() 
                self.state = 'REMOTE_ID'
            elif event == 'datagram-received':
                self.doPing()
                self.state = 'PING'
            elif event == 'shutdown':
                self.doDestroyMe()
                self.state = 'CLOSED'
        #---CLOSED---
        elif self.state == 'CLOSED':
            pass
            
    def isPingOrGreeting(self, arg):
        return arg[0][:2] in [ COMMANDS['PING'], COMMANDS['GREETING'], ] 
            
    def isGreetingOrAlive(self, arg):
        return arg[0][:2] in [ COMMANDS['GREETING'], COMMANDS['ALIVE'], ]
    
    def isAlive(self):
        return time.time() - self.last_alive_packet_time < 60.0 * 1.0 + 5.0
    
    def isIPPortChanged(self):
        if self.remote_idurl is None:
            return False
        ident = identitycache.FromCache(self.remote_idurl)
        new_address = ident.getProtoContact('udp')
        if new_address is None:
            return True
        try:
            ip, port = new_address[6:].split(':')
            new_address = (ip, int(port))
        except:
            return True
        new_address = self.parent.remapAddress(new_address)
        return self.remote_address != new_address                
    
    def doSaveIDURL(self, arg):
        self.remote_idurl = arg
        # dhnio.Dprint(6, 'transport_udp_session.doSaveIDURL [%s] remote idurl is %s' % (str(self.remote_address), self.remote_idurl))
    
    def doRequestRemoteID(self):
        if self.remote_idurl is None:
            self.automat('remote-id-received')
        else:
            identitycache.immediatelyCaching(self.remote_idurl).addCallbacks(
                lambda src: self.automat('remote-id-received', src),
                lambda x: self.automat('remote-id-failed', x))
    
    def doPing(self):
        self.sendDatagram(COMMANDS['PING'])
    
    def doGreeting(self):
        self.sendDatagram(COMMANDS['GREETING']+misc.getLocalID())
    
    def doAlive(self):
        self.sendDatagram(COMMANDS['ALIVE'])
    
    def doReceiveData(self, arg):
        global _ReceiveControlFunc
        io = cStringIO.StringIO(arg[0])
        code = io.read(2)
        cmd = CODES.get(code, None)
        if cmd is None:
            # dhnio.Dprint(2, 'transport_udp_session.doReceiveData WARNING incorrect data from %s: [%s]' % (self.remote_address, code))
            return
        if _ReceiveControlFunc is not None:
            seconds_pause = _ReceiveControlFunc(len(arg[0]))
            if seconds_pause > 0:
                self.client.transport.pauseProducing()
                reactor.callLater(seconds_pause, self.client.transport.resumeProducing)
        # dhnio.Dprint(8, '                                UDP:[%s] from %s' % (cmd, self.remote_address))
        self.last_alive_packet_time = time.time()
        #--- DATA
        if cmd == 'DATA':
            try:
                file_id = struct.unpack('i', io.read(4))[0]
                block_id = struct.unpack('i', io.read(4))[0]
                num_blocks = struct.unpack('i', io.read(4))[0]
                data_size = struct.unpack('i', io.read(4))[0]
            except:
                dhnio.DprintException()
                return
            if not self.incommingFiles.has_key(file_id):
                if self.receivedFiles.has_key(file_id):
                    self.sendDatagram(COMMANDS['REPORT'] + struct.pack('i', file_id) + struct.pack('i', block_id))
                    return
                # self.incommingFiles[file_id] = {}
                self.incommingFiles[file_id] = InboxFile(self, file_id, num_blocks)
            inp_data = io.read()
            if len(inp_data) != data_size:
                dhnio.Dprint(2, 'transport_udp_session.doReceiveData WARNING incorrect datagram received, not full data')
                return
            self.incommingFiles[file_id].input_block(block_id, inp_data) 
            self.sendDatagram(COMMANDS['REPORT'] + struct.pack('i', file_id) + struct.pack('i', block_id))
            # dhnio.Dprint(10, 'transport_udp_session.doReceiveData [%d] (%d/%d) from %s' % (file_id, block_id, num_blocks, self.remote_address))
            if len(self.incommingFiles[file_id].blocks) == num_blocks:
                # dhnio.Dprint(2, 'transport_udp_session.doReceiveData new file [%d] (%d/%d) from %s' % (file_id, block_id, num_blocks, self.remote_address))
                self.incommingFiles[file_id].build()
                file_received(self.incommingFiles[file_id].filename, 'finished', 'udp', self.remote_address)
                self.incommingFiles[file_id].close()   
                del self.incommingFiles[file_id]   
                # self.incommingFiles.pop(file_id, None)
                self.receivedFiles[file_id] = time.time()
                self.eraseOldFileIDs()
        #--- REPORT
        elif cmd == 'REPORT':
            try:
                file_id = struct.unpack('i', io.read(4))[0]
            except:
                dhnio.DprintException()
                return
            if not self.outgoingFiles.has_key(file_id):
                # dhnio.Dprint(2, 'transport_udp_session.doReceiveData WARNING unknown file_id in REPORT packet received from %s: [%d]' % (self.remote_address, file_id))
                return
            try:
                block_id = struct.unpack('i', io.read(4))[0]
            except:
                dhnio.DprintException()
                return
            self.outgoingFiles[file_id].report_block(block_id)
            self.sliding_window.pop((file_id, block_id), None)
            self.sliding_window_size += 1
            if self.sliding_window_size > MAX_WINDOW_SIZE:
                self.sliding_window_size = MAX_WINDOW_SIZE
            if len(self.outgoingFiles[file_id].blocks) == 0:
                self.reportSentDone(file_id)
                self.closeOutboxFile(file_id)
            # dhnio.Dprint(8, 'transport_udp_session.doReceiveData REPORT on [%d,%d] received, blocks=%d, window=%d' % (file_id, block_id, len(self.outgoingFiles[file_id]), self.sliding_window_size))
        #--- GREETING
        elif cmd == 'GREETING':
            greeting_idurl = io.read()
            if greeting_idurl:
                # dhnio.Dprint(6, 'transport_udp_session.doReceiveData got remote idurl from GREETING: %s' % greeting_idurl)
                if self.remote_idurl is None:
                    self.remote_idurl = greeting_idurl
                    dhnio.Dprint(6, 'transport_udp_session.doReceiveData recognized remote idurl from GREETING: %s' % greeting_idurl)
                else:
                    if self.remote_idurl != greeting_idurl:
                        dhnio.Dprint(2, 'transport_udp_session.doReceiveData WARNING incorrect remote idurl in GREETING: %s' % greeting_idurl)
            self.sendDatagram(COMMANDS['ALIVE'])
        #--- PING
        elif cmd == 'PING':
            self.sendDatagram(COMMANDS['GREETING']+misc.getLocalID())
        #--- ALIVE            
        elif cmd == 'ALIVE':
            pass

    def doDestroyMe(self):
        global _SessionsDict
        _SessionsDict.pop(self.remote_address)
        automats.get_automats_by_index().pop(self.index)

    #------------------------------------------------------------------------------ 
    
    def sendDatagram(self, data):
        # dhnio.Dprint(10, '    [UDP] %d bytes to %s (%s)' % (len(data), self.remote_address, nameurl.GetName(self.remote_idurl)))
        if self.client is not None:
            try:
                self.client.transport.write(data, self.remote_address)
                return True
            except:
                return False 
        else:
            dhnio.Dprint(2, 'transport_udp_session.sendDatagram WARNING client is None')
            return False      
        
    def makeFileID(self):
        return int(str(int(time.time() * 100.0))[4:])   
    
    def addOutboxFile(self, filename):
        self.outbox_queue.append(filename)
        # dhnio.Dprint(6, 'transport_udp_session.addOutboxFile [%s], total outbox files: %d' % (os.path.basename(filename), len(self.outbox_queue)))
        
    def putOutboxFile(self, filename):
        self.outbox_queue.insert(0, filename) 
        # dhnio.Dprint(6, 'transport_udp_session.putOutboxFile [%s], total outbox files: %d' % (os.path.basename(filename), len(self.outbox_queue)))
    
    def eraseOldFileIDs(self):
        if len(self.receivedFiles) > 10:
            file_ids = self.receivedFiles.keys()
            cur_tm = time.time()
            for file_id in file_ids:
                if cur_tm - self.receivedFiles[file_id] > 60 * 5:
                    del self.receivedFiles[file_id]
            del file_ids 

    def closeOutboxFile(self, file_id):
        self.outgoingFiles[file_id].close()
        del self.outgoingFiles[file_id]

    def reportSentDone(self, file_id):
        file_sent(self.remote_address, self.outgoingFiles[file_id].filename, 'finished', 'udp')
        self.block_size_level += 1
        if self.block_size_level > MAX_BLOCK_SIZE_LEVEL:
            self.block_size_level = MAX_BLOCK_SIZE_LEVEL
    
    def reportSentFailed(self, file_id):
        file_sent(self.remote_address, self.outgoingFiles[file_id].filename, 'failed', 'udp')
        self.block_size_level -= 2
        if self.block_size_level < 0:
            self.block_size_level = 0

    def processOutboxQueue(self):
        has_reads = False
        while len(self.outbox_queue) > 0 and len(self.outgoingFiles) < self.maxOutgoingFiles:        
            filename = self.outbox_queue.pop(0)
            file_id = self.makeFileID()
            has_reads = True
            # we have a queue of files to be sent
            # somehow file may be removed before we start sending it
            # so we check it here and skip not existed files
            if not os.path.isfile(filename):
                file_sent(self.remote_address, filename, 'failed', 'udp', None, 'file were removed')
                continue
#            if os.access(filename, os.R_OK):
#                file_sent(self.remote_address, filename, 'failed', 'udp', None, 'access denied')
#                continue
            f = OutboxFile(self, self.remote_idurl, file_id, filename)
            f.read_blocks()
            self.outgoingFiles[file_id] = f
        return has_reads

    def processSending(self):
        has_sends = False
        failed_ids = []
        for file_id in self.outgoingFiles.keys():
            if self.outgoingFiles[file_id].send():
                has_sends = True
            if self.outgoingFiles[file_id].has_failed_blocks:
                failed_ids.append(file_id)
        for file_id in failed_ids:
            self.reportSentFailed(file_id)
            self.closeOutboxFile(file_id)
        del failed_ids
        self.checkWindow()
        return has_sends

    def checkWindow(self):
        if len(self.sliding_window) == 0:
            return
        to_remove = [] 
        to_update = {}
        cur_tm = time.time()
        for block_info, tm in self.sliding_window.items():
            if cur_tm - tm < TIME_OUT: # give some time to get an Ack. 
                continue
            to_remove.append(block_info)
            file_id = block_info[0]
            block_id = block_info[1]
            if not self.outgoingFiles.has_key(file_id):
                # dhnio.Dprint(2, 'transport_udp_session.checkWindow WARNING unknown file_id [%d] from %s' % (file_id, nameurl.GetName(self.remote_idurl)))
                continue
            if not self.outgoingFiles[file_id].blocks.has_key(block_id):
                dhnio.Dprint(2, 'transport_udp_session.checkWindow WARNING unknown block_id: %d' % block_id)
                continue
            self.outgoingFiles[file_id].send_block(block_id)
            isFailed = self.outgoingFiles[file_id].mark_failed_block(block_id)
            if not isFailed:
                to_update[block_info] = cur_tm
        for block_info in to_remove:
            del self.sliding_window[block_info]
            # dhnio.Dprint(8, 'transport_udp_session.doCheckWindow (%d,%d) removed, window=%d' % (file_id, block_id, len(self.sliding_window)))
        for block_info, tm in to_update.items():
            self.sliding_window[block_info] = tm
            # dhnio.Dprint(8, 'transport_udp_session.doCheckWindow (%s) resending to %s, window=%d' % (block_info, self.remote_address, len(self.sliding_window)))
        if len(to_remove) > 0:
            self.sliding_window_size = int( self.sliding_window_size / 2.0 )
            if self.sliding_window_size < MIN_WINDOW_SIZE:
                self.sliding_window_size = MIN_WINDOW_SIZE
            # dhnio.Dprint(8, 'transport_udp_session.doCheckWindow decreased, window=%d' % self.sliding_window_size)
        del to_remove
        del to_update

#------------------------------------------------------------------------------ 
    
def check_outbox_queue():    
    global _SessionsDict
    has_reads = False
    for sess in _SessionsDict.values():
        if sess.processOutboxQueue():
            has_reads = True
    return has_reads 
    
def process_outbox_queue():
    global _OutboxQueueDelay
    global _OutboxQueueTask
    
    has_reads = check_outbox_queue()

    _OutboxQueueDelay = misc.LoopAttenuation(
        _OutboxQueueDelay, 
        has_reads, 
        settings.MinimumSendingDelay(), 
        settings.MaximumSendingDelay(),)
    
    # attenuation
    _OutboxQueueTask = reactor.callLater(_OutboxQueueDelay, process_outbox_queue)
        

def process_sending():
    global _SendingDelay
    global _SendingTask
    global _SessionsDict
    
    has_sends = False
    for sess in _SessionsDict.values():
        if sess.processSending():
            has_sends = True
    
    _SendingDelay = misc.LoopAttenuation(
        _SendingDelay, 
        has_sends, 
        settings.MinimumSendingDelay(), 
        settings.MaximumSendingDelay(),)
    
    # attenuation
    _SendingTask = reactor.callLater(_SendingDelay, process_sending)
    
#------------------------------------------------------------------------------ 

def sessions():
    global _SessionsDict
    return _SessionsDict.keys()


def is_session_opened(address, idurl=None):
    global _SessionsDict
    if _SessionsDict.has_key(address):
        return True
    return False
        

def outbox_file(address, idurl, filename, fast=False):
    global _SessionsDict
#    dhnio.Dprint(6, 'transport_udp_session.outbox_file %s to %s (%s)' % (
#        os.path.basename(filename), nameurl.GetName(idurl), str(address)))
    s = open_session(address, idurl)
    if fast:
        s.putOutboxFile(filename)
    else:
        s.addOutboxFile(filename)
    check_outbox_queue()


def big_event(event, arg=None):
    global _SessionsDict
    for address in _SessionsDict.keys():
        A(address, event, arg)


def data_received(datagram, address):
    try:
        from transport_control import black_IPs_dict
        if address[0] in black_IPs_dict().keys():
            dhnio.Dprint(6, 'transport_udp_session.data_received %d bytes from BLACK IP: %s, %s' % (len(datagram), str(address[0]), str(black_IPs_dict()[address[0]])) )
            return
    except:
        pass
    if address not in sessions():
        open_session(address, None)
    A(address, 'datagram-received', (datagram, address))


def shutdown_all():
    big_event('shutdown')
    
    
def file_received(filename, status, proto='', host=None, error=None, message=''):
    global _ReceiveStatusCallback
    if _ReceiveStatusCallback is not None:
        _ReceiveStatusCallback(filename, status, proto, host, error, message)
    
    
def file_sent(host, filename, status, proto='', error=None, message=''):
    global _SendStatusCallback
    if _SendStatusCallback is not None:
        _SendStatusCallback(host, filename, status, proto, error, message)


def timer30sec():
    global _Timer30sec
    big_event('timer-30sec')
    _Timer30sec = reactor.callLater(random.randint(25,35), timer30sec)


def timer10sec():
    global _Timer10sec
    big_event('timer-10sec')
    _Timer10sec = reactor.callLater(random.randint(5,15), timer10sec)


def timer1sec():
    global _Timer1sec
    big_event('timer-1sec')
    _Timer1sec = reactor.callLater(1, timer1sec)
    
#------------------------------------------------------------------------------ 
    
def SetReceiveStatusCallback(cb):
    global _ReceiveStatusCallback
    _ReceiveStatusCallback = cb
    
    
def SetSendStatusCallback(cb):
    global _SendStatusCallback
    _SendStatusCallback = cb
    
def SetSendControlFunc(f):
    global _SendControlFunc
    _SendControlFunc = f
    
def SetReceiveControlFunc(f):
    global _ReceiveControlFunc
    _ReceiveControlFunc = f

def SetRegisterTransferFunc(f):
    global _RegisterTransferFunc
    _RegisterTransferFunc = f

def SetUnRegisterTransferFunc(f):
    global _UnRegisterTransferFunc
    _UnRegisterTransferFunc = f
    
#------------------------------------------------------------------------------ 

    
def StartTimers():
    global _Timer30sec
    global _Timer10sec
    global _Timer1sec
    if _Timer30sec is None:
        timer30sec()
    if _Timer10sec is None: 
        timer10sec()
    if _Timer1sec is None:
        timer1sec()


def StopTimers():
    global _Timer30sec
    global _Timer10sec
    global _Timer1sec
    if _Timer30sec:
        _Timer30sec.cancel()
        _Timer30sec = None
    if _Timer10sec:
        _Timer10sec.cancel()
        _Timer10sec = None
    if _Timer1sec:
        _Timer1sec.cancel()
        _Timer1sec = None





