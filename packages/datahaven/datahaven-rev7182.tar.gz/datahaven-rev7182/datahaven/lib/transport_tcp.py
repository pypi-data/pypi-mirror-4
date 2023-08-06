#!/usr/bin/python
#transport_tcp.py
#
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2012
#    Use of this software constitutes acceptance of the Terms of Use
#      http://datahaven.net/terms_of_use.html
#    All rights reserved.
#
#


import os
import sys
import time

if __name__ == '__main__':
    sys.path.insert(0, os.path.abspath('..'))


try:
    from twisted.internet import reactor
except:
    sys.exit('Error initializing twisted.internet.reactor in transport_tcp.py')


from twisted.internet import task
from twisted.internet import protocol
#from twisted.internet.protocol import ServerFactory, ClientFactory
from twisted.protocols import basic
from twisted.internet.defer import Deferred, fail 
from twisted.python import log


import dhnio
import misc
import tmpfile

_SendStatusFunc = None
_ReceiveStatusFunc = None
_SendControlFunc = None
_ReceiveControlFunc = None
_RegisterTransferFunc = None
_UnRegisterTransferFunc = None

#------------------------------------------------------------------------------

def init(   sendStatusFunc=None, 
            receiveStatusFunc=None, 
            sendControl=None, 
            receiveControl=None,
            registerTransferFunc=None,
            unregisterTransferFunc=None):
    dhnio.Dprint(4, 'transport_tcp.init')
    global _SendStatusFunc
    global _ReceiveStatusFunc
    global _RegisterTransferFunc
    global _UnRegisterTransferFunc
    if sendStatusFunc is not None:
        _SendStatusFunc = sendStatusFunc
    if receiveStatusFunc is not None:
        _ReceiveStatusFunc = receiveStatusFunc
    if sendControl is not None:
        _SendControlFunc = sendControl 
    if registerTransferFunc is not None:
        _RegisterTransferFunc = registerTransferFunc
    if unregisterTransferFunc is not None:
        _UnRegisterTransferFunc = unregisterTransferFunc
    

def send(filename, host, port, do_status_report=True, send_control_func=None, result_defer=None):
    global _SendControlFunc
    if not os.path.isfile(filename):
        if result_defer is not None:
            result_defer.errback('failed')
        return
    #dhnio.Dprint(12, "transport_tcp.send %s %s %s" %(str(host), str(port), os.path.basename(filename)))
    sender = MySendingFactory(
        filename, host, int(port), 
        result_defer=result_defer, 
        do_status_report=do_status_report, 
        send_control_func=(send_control_func or _SendControlFunc))
    reactor.connectTCP(host, int(port), sender)


def receive(port, receive_control_func=None):
    global _ReceiveControlFunc
    dhnio.Dprint(8, "transport_tcp.receive going to listen on port "+ str(port))

    def _try_receiving(port, count, receive_control_func):
        dhnio.Dprint(10, "transport_tcp.receive count=%d" % count)
        f = MyReceiveFactory(receive_control_func)
        try:
            mylistener = reactor.listenTCP(int(port), f)
        except:
            mylistener = None
            dhnio.DprintException()
        return mylistener

    def _loop(port, result, count, receive_control_func):
        l = _try_receiving(port, count, receive_control_func)
        if l is not None:
            dhnio.Dprint(8, "transport_tcp.receive started on port "+ str(port))
            result.callback(l)
            return
        if count > 10:
            dhnio.Dprint(1, "transport_tcp.receive WARNING port %s is busy!" % str(port))
            result.errback(None)
            return
        reactor.callLater(1, _loop, port, result, count+1, receive_control_func)

    res = Deferred()
    _loop(port, res, 0, receive_control_func or _ReceiveControlFunc)
    return res

#------------------------------------------------------------------------------

class MyFileSender(basic.FileSender):
    
    def __init__(self, protocol):
        self.protocol = protocol
        self.bytesLastRead = 0
    
    def resumeProducing(self):
        #sys.stdout.write('=')
        chunk = ''
        if self.file:
            more_bytes = self.CHUNK_SIZE
            if self.protocol.factory.send_control_func:
                more_bytes = self.protocol.factory.send_control_func(self.bytesLastRead, self.CHUNK_SIZE)
            chunk = self.file.read(more_bytes)
            self.bytesLastRead = len(chunk)
        # print len(chunk)
        if not chunk:
            self.file = None
            self.bytesLastRead = 0
            self.consumer.unregisterProducer()
            if self.deferred:
                self.deferred.callback(self.lastSent)
                self.deferred = None
            return
        if self.transform:
            chunk = self.transform(chunk)
        self.consumer.write(chunk)
        self.lastSent = chunk[-1]


# In Putter "self.factory" references the parent object, so we can
# access arguments like "host", "port", and "filename"
class MySendingProtocol(protocol.Protocol):
    fin = None
    sentBytes = 0
    transfer_id = None
    
    def getSentBytes(self):
        return self.sentBytes
    
    def connectionMade(self):
        global _SendStatusFunc
        global _RegisterTransferFunc
        if not os.path.isfile(self.factory.filename):
            dhnio.Dprint(6, 'transport_tcp.Putter.connectionMade WARNING file %s was not found but we get connected to the %s' % (self.factory.filename, self.factory.host))
            if self.factory.do_status_report:
                _SendStatusFunc(self.transport.getPeer(), self.factory.filename,
                    'failed', 'tcp', None, 'file was not found')
            self.transport.loseConnection()
            if self.factory.result_defer is not None:
                if not self.factory.result_defer.called:
                    self.factory.result_defer.errback('failed')
                    self.factory.result_defer = None
            return
        try:
            sz = os.path.getsize(self.factory.filename)
            self.fin = open(self.factory.filename, 'rb')
        except:
            dhnio.DprintException()
            if self.factory.do_status_report:
                _SendStatusFunc(self.transport.getPeer(), self.factory.filename,
                    'failed', 'tcp', None, 'error opening file')
            self.transport.loseConnection()
            if self.factory.result_defer is not None:
                if not self.factory.result_defer.called:
                    self.factory.result_defer.errback('failed')
                    self.factory.result_defer = None
            return

        self.fileSender = MyFileSender(self)
        d = self.fileSender.beginFileTransfer(self.fin, self.transport, self.transformData)
        d.addCallback(self.finishedTransfer)
        d.addErrback(self.transferFailed)
        self.transfer_id = _RegisterTransferFunc(
            'send', (self.transport.getPeer().host, int(self.transport.getPeer().port)), 
            self.getSentBytes, self.factory.filename, sz)

    def transformData(self, data):
        self.sentBytes += len(data)
        # self.factory.registerWritten(len(data))
        # sys.stdout.write('.') # print len(data)
        return data

    def finishedTransfer(self, result):
        global _SendStatusFunc
        try:
            self.fin.close()
        except:
            dhnio.Dprint(1, 'transport_tcp.Putter.finishedTransfer ERROR close file failed')

        if self.factory.do_status_report:
            _SendStatusFunc(self.transport.getPeer(), self.factory.filename, 'finished', 'tcp')
        self.transport.loseConnection()
        if self.factory.result_defer is not None:
            if not self.factory.result_defer.called:
                self.factory.result_defer.callback('finished')
                self.factory.result_defer = None

    def transferFailed(self, err):
        global _SendStatusFunc
        dhnio.Dprint(1, 'transport_tcp.Putter.transferFailed NETERROR host=' + self.factory.host + " file=" + self.factory.filename)
        try:
            self.fin.close()
            dhnio.Dprint (14, 'transport_tcp.Putter.transferFailed - close file')
        except:
            dhnio.Dprint (1, 'transport_tcp.Putter.transferFailed ERROR closing file')

        if self.factory.do_status_report:
            _SendStatusFunc(self.transport.getPeer(), self.factory.filename, 'failed', 'tcp', err, 'transfer failed')
            # not so good

        self.transport.loseConnection()
        if self.factory.result_defer is not None:
            if not self.factory.result_defer.called:
                self.factory.result_defer.errback('failed')
                self.factory.result_defer = None

    def connectionLost(self, reason):
        global _UnRegisterTransferFunc
        if self.transfer_id is not None:
            _UnRegisterTransferFunc(self.transfer_id)
        # dhnio.Dprint(6, 'transport_tcp.MySendingProtocol.connectionLost with %s' % str(self.transport.getPeer()))
        self.transport.loseConnection()
        try:
            self.fin.close()
        except:
            pass

class MySendingFactory(protocol.ClientFactory):
    def __init__(self, filename, host, port, result_defer=None, do_status_report=True, send_control_func=None):
        self.filename = filename
        self.host = host
        self.port = port
        self.protocol = MySendingProtocol
        self.result_defer = result_defer
        self.do_status_report = do_status_report
        self.send_control_func = send_control_func # callback which reads from the file 

    def clientConnectionFailed(self, connector, reason):
        global _SendStatusFunc
        protocol.ClientFactory.clientConnectionFailed(self, connector, reason)
        if self.do_status_report:
            _SendStatusFunc(connector.getDestination(),
                self.filename, 'failed', 'tcp', reason, 'connection failed')
        if self.result_defer is not None:
            if not self.result_defer.called:
                self.result_defer.errback('failed')
                self.result_defer = None
        name = str(reason.type.__name__)
        dhnio.Dprint(10, 'transport_tcp.clientConnectionFailed NETERROR [%s] with %s:%s' % (
            name,
            connector.getDestination().host,
            connector.getDestination().port,))

#------------------------------------------------------------------------------

class MyReceiveProtocol(protocol.Protocol):
    filename = ""     # string with path/filename
    fd = ""           # integer file descriptor like os.open() returns
    peer = ""
    receivedBytes = 0
    transfer_id = None

    def getReceivedBytes(self):
        return self.receivedBytes
    
    def connectionMade(self):
        global _RegisterTransferFunc
        if self.peer == "":
            self.peer = self.transport.getPeer()
        else:
            if self.peer != self.transport.getPeer():
                dhnio.Dprint(1, "transport_tcp.connectionMade NETERROR thought we had one object per connection")
        try:
            from transport_control import black_IPs_dict
            if self.peer.host in black_IPs_dict().keys():
                dhnio.Dprint(12, 'transport_tcp.connectionMade from BLACK IP: %s, %s' % (str(self.peer.host), str(black_IPs_dict()[self.peer.host])) )
                self.transport.loseConnection()
                return
        except:
            pass
        if self.filename == "":
            self.fd, self.filename = tmpfile.make("tcp-in")
        else:   
            raise Exception("transport_tcp.ReceiveFiles has second connection in same object")
        self.transfer_id = _RegisterTransferFunc(
            'receive', (self.transport.getPeer().host, int(self.transport.getPeer().port)), 
            self.getReceivedBytes, self.filename, -1)

    def dataReceived(self, data):
        amount = len(data)
        os.write(self.fd, data)
        self.receivedBytes += amount
        if self.factory.receive_control_func is not None:
            seconds_pause = self.factory.receive_control_func(len(data))
            if seconds_pause > 0:
                # print '                      paused for', seconds_pause, 'seconds'
                self.transport.pauseProducing()
                reactor.callLater(seconds_pause, self.transport.resumeProducing)

    def connectionLost(self, reason):
        global _ReceiveStatusFunc
        global _UnRegisterTransferFunc
        if self.transfer_id is not None:
            _UnRegisterTransferFunc(self.transfer_id)
        # dhnio.Dprint(6, 'transport_tcp.MyReceiveProtocol.connectionLost with %s' % str(self.transport.getPeer()))
        os.close(self.fd)
        _ReceiveStatusFunc(self.filename, "finished", 'tcp', self.transport.getPeer(), reason)


class MyReceiveFactory(protocol.ServerFactory):
    def __init__(self, receive_control_func):
        self.receive_control_func = receive_control_func
        
    def buildProtocol(self, addr):
        p = MyReceiveProtocol()
        p.factory = self
        return p

#------------------------------------------------------------------------------

def SendStatusFuncDefault(host, filename, status, proto='', error=None, message=''):
    try:
        from transport_control import sendStatusReport
        sendStatusReport(host, filename, status, proto, error, message)
    except:
        dhnio.DprintException()

def ReceiveStatusFuncDefault(filename, status, proto='', host=None, error=None, message=''):
    try:
        from transport_control import receiveStatusReport
        receiveStatusReport(filename, status, proto, host, error, message)
    except:
        dhnio.DprintException()

def SendControlFuncDefault(prev_read, chunk_size):
    return chunk_size

def ReceiveControlFuncDefault(new_data_size):
    return 0

def RegisterTransferFuncDefault(send_or_receive, remote_address, callback, filename, size):
    try:
        from transport_control import register_transfer
        return register_transfer('tcp', send_or_receive, remote_address, callback, filename, size)
    except:
        dhnio.DprintException()
        return None
    
def UnRegisterTransferFuncDefault(transfer_id):
    try:
        from transport_control import unregister_transfer
        return unregister_transfer(transfer_id)
    except:
        dhnio.DprintException()
    return None

_SendStatusFunc = SendStatusFuncDefault
_ReceiveStatusFunc = ReceiveStatusFuncDefault
_SendControlFunc = SendControlFuncDefault
_ReceiveControlFunc = ReceiveControlFuncDefault
_RegisterTransferFunc = RegisterTransferFuncDefault
_UnRegisterTransferFunc = UnRegisterTransferFuncDefault


#-------------------------------------------------------------------------------

def usage():
        print '''
args:
transport_tcp.py [port]                                   -  to receive
transport_tcp.py [host] [port] [file name]                -  to send a file
transport_tcp.py [host] [port] [file name] [interval]     -  to start sending continously
'''



def mytest():
    dhnio.SetDebug(18)

    filename = "transport_tcp.pyc"              # just some file to send
##    host = "work.offshore.ai"
##    host = "89.223.30.208"
    host = 'localhost'
    port = 7771

    if len(sys.argv) == 4:
        send(sys.argv[3], sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 2:
        r = receive(sys.argv[1])
        print r
    else:
        usage()
        sys.exit()
    reactor.run()

bytes_counter = 0
time_counter = time.time()
count_period = 1
current_chunk = 1

def _my_receive_control(new_data_size):
    try:
        from transport_control import ReceiveTrafficControl
        return ReceiveTrafficControl(new_data_size)
    except:
        dhnio.DprintException()
        return 0
    
def _my_send_control(prev_read_size, chunk_size):
    try:
        from transport_control import SendTrafficControl
        return SendTrafficControl(prev_read_size, chunk_size)
    except:
        dhnio.DprintException()
        return chunk_size

def _my_monitor():
    src = ''
    for address in transfers().keys():
        for obj in transfers()[address]['send']:
            src += '%d to %s, ' % (obj.sentBytes, str(address))
        for obj in transfers()[address]['receive']:
            src += '%d from %s, ' % (obj.receivedBytes, str(address))
    print '>>>', src
    reactor.callLater(1, _my_monitor)

if __name__ == "__main__":
    #import datahaven.p2p.memdebug as memdebug
    #memdebug.start(8080)
    dhnio.SetDebug(20)
    dhnio.LifeBegins()

    from twisted.internet.defer import setDebugging
    setDebugging(True)

    reactor.callLater(1, _my_monitor)

    if len(sys.argv) == 2:
        r = receive(sys.argv[1], receive_control_func=_my_receive_control)
        reactor.run()
    elif len(sys.argv) == 4:
        send(sys.argv[3], sys.argv[1], sys.argv[2], send_control_func=_my_send_control).addBoth(lambda x: dhnio.Dprint(2, 'RESULT:%s'%str(x)))
        reactor.run()
    elif len(sys.argv) == 5:
        l = task.LoopingCall(send, sys.argv[3], sys.argv[1], sys.argv[2])
        l.start(float(sys.argv[4]))
        reactor.run()
    else:
        usage()

