#!/usr/bin/python
#transport_udp_session.py
#
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2012
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
import misc
import identity
import identitycache
import tmpfile 
import nameurl

import automat
import automats
import transport_udp

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

_SessionsDict = {}

_ReceiveStatusCallback = None
_SendStatusCallback = None

_Timer1sec = None
_Timer10sec = None
_Timer30sec = None

#------------------------------------------------------------------------------ 

def A(address, event=None, arg=None):
    global _SessionsDict
    if not _SessionsDict.has_key(address):
        _SessionsDict[address] = TransportUDPSession(
            address, 'udp_session_%s:%s' % (address[0], address[1]), 'AT_STARTUP', 10)
    if event is not None:
        _SessionsDict[address].automat(event, arg)
    return _SessionsDict[address]
      

class TransportUDPSession(automat.Automat):
    timers = {#'timer-1min':     (60,    ['CONNECTED', 'SENDING']),
              #'timer-30sec':    (30,    ['GREETING', 'PING', 'DISCONNECTED']),
              #'timer-1sec':     (1,     ['PING', 'GREETING', 'CONNECTED']),
              'timer-01sec':    (0.1,   ['SENDING', 'WAITING'])}
    def __init__(self, address, name, state, debug_level):
        self.remote_address = address
        self.remote_idurl = None
        self.parent = None
        self.client = None
        self.last_alive_packet_time = 0
        self.incommingFiles = {}
        self.outgoingFiles = {}
        self.receivedFiles = {}
        self.outbox_queue = []
        self.tries = 0
        self.current_filename = ''
        self.current_file_id = None
        self.current_block_id = -1
        self.current_blocks = 0
        self.sliding_window = {}
        self.sliding_window_size = MIN_WINDOW_SIZE
        self.failedBlocks = {}
        self.hasFailedBlocks = False
        self.block_size_level = 0
        automat.Automat.__init__(self, name, state, debug_level)
        
    def A(self, event, arg):
        #---AT_STARTUP---
        if self.state == 'AT_STARTUP':
            if event == 'init':
                self.doSaveIDURLAndParent(arg)
                self.doRequestRemoteID()
                self.state = 'REMOTE_ID'
        #---SENDING---
        elif self.state == 'SENDING':
            if event == 'timer-01sec' and self.isMoreBlocks() and self.isWindowOpen():
                self.doSendBlocks() 
                self.doCheckWindow()               
            elif ( event == 'timer-01sec' and not self.isFailedBlocks() ) and ( not self.isWindowOpen() or ( not self.isMoreBlocks() and not self.isAllSent() ) ):
                self.doCheckWindow()
            elif ( event == 'timer-01sec' and self.isFailedBlocks() ) or ( event == 'timer-30sec' and not self.isAlive() ):
                self.doReportFailed()
                self.doCloseFile()
                self.state = 'CONNECTED'
            elif event == 'timer-01sec' and not self.isMoreBlocks() and self.isAllSent():
                self.doReportDone()
                self.doCloseFile()
                self.state = 'CONNECTED'
            elif event == 'datagram-received':
                self.doReceiveData(arg)
            elif event == 'shutdown':
                self.doReportFailed()
                self.doCloseFile()
                self.doDestroyMe()
                self.state = 'CLOSED'
        #---REMOTE_ID---
        elif self.state == 'REMOTE_ID':
            if event == 'remote-id-received' and not self.isIPPortChanged():
                self.doPing()
                self.state = 'PING'
            elif event == 'remote-id-received' and self.isIPPortChanged():
                self.parent.A('ip-port-changed', self.remote_idurl)
                #transport_udp.A('ip-port-changed', self.remote_idurl)
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
        #---CONNECTED---
        elif self.state == 'CONNECTED':
            if event == 'datagram-received':
                self.doReceiveData(arg)
            elif event == 'timer-1sec' and self.isOutgoingFiles():
                self.doReadFile()
                self.tries = 0
                self.state = 'SENDING'
            elif event == 'timer-30sec' and self.isAlive():
                self.doAlive()
            elif event == 'timer-30sec' and not self.isAlive():
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
        return arg[0] in [ COMMANDS['PING'], COMMANDS['GREETING'], ] 
            
    def isGreetingOrAlive(self, arg):
        return arg[0] in [ COMMANDS['GREETING'], COMMANDS['ALIVE'], ]
    
    def isAlive(self):
        return time.time() - self.last_alive_packet_time < 60.0 * 1.0 + 5.0
    
    def isOutgoingFiles(self):
        return len(self.outbox_queue) > 0
    
    def isAllSent(self):
        return len(self.outgoingFiles[self.current_file_id]) == 0
    
    def isMoreBlocks(self):
        return self.current_block_id < self.current_blocks
        #return self.blocksReports[self.current_file_id] >= self.current_blocks
    
    def isIPPortChanged(self):
        ident = identitycache.FromCache(self.remote_idurl)
        new_contact = ident.getProtoContact('udp')
        if new_contact is None:
            return True
        try:
            ip, port = new_contact[6:].split(':')
            port = int(port)
        except:
            return True
        return self.remote_address != (ip, port)                
    
#    def isTimePassed(self):
#        return time.time() - self.current_try > 10
    
    def isWindowOpen(self):
        return len(self.sliding_window) < self.sliding_window_size
    
    def isFailedBlocks(self):
        return self.hasFailedBlocks
    
    def doSaveIDURLAndParent(self, arg):
        self.parent = arg[0]
        self.client = self.parent.client
        self.remote_idurl = arg[1]
    
    def doRequestRemoteID(self):
        identitycache.immediatelyCaching(self.remote_idurl).addCallbacks(
            lambda src: self.automat('remote-id-received', src),
            lambda x: self.automat('remote-id-failed', x))
    
    def doPing(self):
        self.sendDatagram(COMMANDS['PING'])
    
    def doGreeting(self):
        self.sendDatagram(COMMANDS['GREETING'])
    
    def doAlive(self):
        self.sendDatagram(COMMANDS['ALIVE'])
    
    def doReceiveData(self, arg):
        io = cStringIO.StringIO(arg[0])
        code = io.read(2)
        cmd = CODES.get(code, None)
        if cmd is None:
            # dhnio.Dprint(2, 'transport_udp_session.doReceiveData WARNING incorrect data from %s: [%s]' % (self.remote_address, code))
            return
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
                self.incommingFiles[file_id] = {}
            inp_data = io.read()
            if len(inp_data) != data_size:
                dhnio.Dprint(2, 'transport_udp_session.doReceiveData WARNING incorrect datagram received, not full data')
                return
            self.incommingFiles[file_id][block_id] = inp_data 
            self.sendDatagram(COMMANDS['REPORT'] + struct.pack('i', file_id) + struct.pack('i', block_id))
            # dhnio.Dprint(10, 'transport_udp_session.doReceiveData [%d] (%d/%d) from %s' % (file_id, block_id, num_blocks, self.remote_address))
            if len(self.incommingFiles[file_id]) == num_blocks:
                self.buildInboxFile(file_id)
                del self.incommingFiles[file_id]
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
            if not self.outgoingFiles[file_id].has_key(block_id):
                # dhnio.Dprint(2, 'transport_udp_session.doReceiveData WARNING unknown block_id in REPORT packet received from %s: [%d]' % (self.remote_address, block_id))
                return
            del self.outgoingFiles[file_id][block_id]
            self.sliding_window.pop((file_id, block_id), None)
            self.sliding_window_size += 1
            if self.sliding_window_size > MAX_WINDOW_SIZE:
                self.sliding_window_size = MAX_WINDOW_SIZE
            # dhnio.Dprint(8, 'transport_udp_session.doReceiveData REPORT on [%d,%d] received, blocks=%d, window=%d' % (file_id, block_id, len(self.outgoingFiles[file_id]), self.sliding_window_size))
        #--- GREETING
        elif cmd == 'GREETING':
            self.sendDatagram(COMMANDS['ALIVE'])
        #--- PING
        elif cmd == 'PING':
            self.sendDatagram(COMMANDS['GREETING'])
        #--- ALIVE            
        elif cmd == 'ALIVE':
            pass

    def doReadFile(self):
        self.current_filename = self.outbox_queue.pop(0)
        self.current_file_id = self.makeFileID()
        self.outgoingFiles[self.current_file_id] = {}
#        self.blocksReports[self.current_file_id] = 0
        fin = open(self.current_filename, 'rb')
        block_id = 0
        while True:
            block_data = fin.read(BLOCK_SIZE_LEVELS[self.block_size_level])
            if block_data == '':
                break
            self.outgoingFiles[self.current_file_id][block_id] = block_data
            block_id += 1    
        fin.close()     
        self.current_block_id = 0     
        self.current_blocks = block_id  
        # dhnio.Dprint(6, 'transport_udp_session.doReadFile file_id=%d, blocks=%d' % (
        #     self.current_file_id, len(self.outgoingFiles[self.current_file_id])))
    
    def doCheckWindow(self):
        if len(self.sliding_window) == 0:
            return
        # dhnio.Dprint(14, 'transport_udp_session.doCheckWindow has %d items' % len(self.sliding_window))
        to_remove = [] 
        to_update = {}
        cur_tm = time.time()
        for block_info, tm in self.sliding_window.items():
            if cur_tm - tm < TIME_OUT: # give some time to get an Ack. 
                continue
            to_remove.append(block_info)
            file_id = block_info[0]
            block_id = block_info[1]
            if file_id != self.current_file_id:
                continue
            if not self.outgoingFiles.has_key(file_id):
                dhnio.Dprint(2, 'transport_udp_session.doCheckWindow WARNING unknown file_id: %d' % file_id)
                continue
            if not self.outgoingFiles[file_id].has_key(block_id):
                dhnio.Dprint(2, 'transport_udp_session.doCheckWindow WARNING unknown block_id: %d' % block_id)
                continue
            self.sendBlock(block_id)
            isFailed = self.markFailedBlock(block_id)
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
        
    def doSendBlocks(self):
        while len(self.sliding_window) < self.sliding_window_size and self.current_block_id < self.current_blocks:
            if not self.sendBlock(self.current_block_id):
                break
            self.sliding_window[(self.current_file_id, self.current_block_id)] = time.time()
            self.current_block_id += 1
    
    def doCloseFile(self):
        del self.outgoingFiles[self.current_file_id]
        self.failedBlocks.pop(self.current_file_id, None)
        # dhnio.Dprint(6, 'transport_udp_session.doCloseFile [%d] closed' % self.current_file_id)
        self.current_file_id = None
        self.current_filename = ''
        self.current_block_id = -1
        self.current_blocks = 0
        self.hasFailedBlocks = False
        
    def doReportDone(self):    
        # dhnio.Dprint(6, 'transport_udp_session.doReportDone [%s] finished to %s' % (os.path.basename(self.current_filename), self.remote_address))
        file_sent(self.remote_address, self.current_filename, 'finished', 'udp')
        self.block_size_level += 1
        if self.block_size_level > MAX_BLOCK_SIZE_LEVEL:
            self.block_size_level = MAX_BLOCK_SIZE_LEVEL
        
    def doReportFailed(self):
        # dhnio.Dprint(6, 'transport_udp_session.doReportFailed [%s] failed to %s' % (os.path.basename(self.current_filename), self.remote_address))
        file_sent(self.remote_address, self.current_filename, 'failed', 'udp', None, 'sending failed')
        self.block_size_level -= 2
        if self.block_size_level < 0:
            self.block_size_level = 0

    def doDestroyMe(self):
        global _SessionsDict
        _SessionsDict.pop(self.remote_address)
        automats.get_automats_by_index().pop(self.index)
    
    def sendDatagram(self, data):
        if self.client is not None:
            try:
                self.client.transport.write(data, self.remote_address)
                return True
            except:
                return False 
        else:
            dhnio.Dprint(2, 'transport_udp_session.sendDatagram WARNING client is None')
            return False      
        
    def incommingFileDone(self):
        file_received(self.filename_in, 'finished', 'udp', self.remote_address)
        os.close(self.fd_in)
        self.fd_in = None
        self.filename_in = ''             
        
    def makeFileID(self):
        return int(str(int(time.time() * 100.0))[4:])   
    
    def addOutboxFile(self, filename):
        self.outbox_queue.append(filename)
        
    def putOutboxFile(self, filename):
        self.outbox_queue.insert(0, filename) 
    
    def buildInboxFile(self, file_id):
        fd, filename = tmpfile.make("udp-in")
        for block_id in range(len(self.incommingFiles[file_id])):
            data = self.incommingFiles[file_id][block_id]
            os.write(fd, data)
        os.close(fd)
        file_received(filename, 'finished', 'udp', self.remote_address)   
    
    def sendBlock(self, block_id):
        data = self.outgoingFiles[self.current_file_id][block_id]
        datagram = COMMANDS['DATA']
        datagram += struct.pack('i', self.current_file_id)
        datagram += struct.pack('i', block_id)
        datagram += struct.pack('i', self.current_blocks)
        datagram += struct.pack('i', len(data))
        datagram += data
        return self.sendDatagram(datagram)
#        dhnio.Dprint(8, 'transport_udp_session.sendBlock [%d,%d] (%d bytes) window=%d' % (
#            self.current_file_id, block_id, len(datagram), len(self.sliding_window)))
         
    def markFailedBlock(self, block_id):
        if not self.failedBlocks.has_key(self.current_file_id):
            self.failedBlocks[self.current_file_id] = {}
        if not self.failedBlocks[self.current_file_id].has_key(block_id):
            self.failedBlocks[self.current_file_id][block_id] = 0
        self.failedBlocks[self.current_file_id][block_id] += 1
        if self.failedBlocks[self.current_file_id][block_id] >= BLOCK_RETRIES:
            self.hasFailedBlocks = True
            # dhnio.Dprint(8, 'transport_udp_session.markFailedBlock (%d,%d) is failed to send' % (self.current_file_id, block_id))
            return True
        return False

    def eraseOldFileIDs(self):
        if len(self.receivedFiles) > 10:
            file_ids = self.receivedFiles.keys()
            cur_tm = time.time()
            for file_id in file_ids:
                if cur_tm - self.receivedFiles[file_id] > 60 * 5:
                    del self.receivedFiles[file_id]
            del file_ids 
    
#------------------------------------------------------------------------------ 

def sessions():
    global _SessionsDict
    return _SessionsDict.keys()


def outbox_file(addres, filename, fast=False):
    global _SessionsDict
    if _SessionsDict.has_key(addres):
        if fast:
            _SessionsDict[addres].putOutboxFile(filename)
        else:
            _SessionsDict[addres].addOutboxFile(filename)


def big_event(event, arg=None):
    global _SessionsDict
    for address in _SessionsDict.keys():
        A(address, event, arg)


def data_received(datagram, address):
    global _SessionsDict
    sess = _SessionsDict.get(address, None)
    if sess is not None:
        sess.automat('datagram-received', (datagram, address))
        

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





