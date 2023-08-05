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


if __name__ == '__main__':
    sys.path.insert(0, os.path.abspath('..'))


try:
    from twisted.internet import reactor
except:
    sys.exit('Error initializing twisted.internet.reactor in transport_tcp.py')


from twisted.internet import task
from twisted.internet import protocol
from twisted.internet.protocol import ServerFactory, ClientFactory
from twisted.protocols import basic
from twisted.internet.defer import Deferred
from twisted.python import log


import dhnio
import misc
import tmpfile

#------------------------------------------------------------------------------

def init(sendStatusFunc=None, receiveStatusFunc=None):
    dhnio.Dprint(4, 'transport_tcp.init')
    global _SendStatusFunc
    global _ReceiveStatusFunc
    if sendStatusFunc is not None:
        _SendStatusFunc = sendStatusFunc
    if receiveStatusFunc is not None:
        _ReceiveStatusFunc = receiveStatusFunc


def send(filename, host, port, do_status_report=True):
    d = Deferred()
    if not os.path.isfile(filename):
        try:
            d.errback('failed')
        except:
            dhnio.DprintException()
        return d
    #dhnio.Dprint(12, "transport_tcp.send %s %s %s" %(str(host), str(port), os.path.basename(filename)))
    sender = SendingFactory(filename, host, int(port), d, do_status_report)
    reactor.connectTCP(host, int(port), sender)
    return d


def receive(port):
    dhnio.Dprint(8, "transport_tcp.receive going to listen on port "+ str(port))

    def _try_receiving(port, count):
        dhnio.Dprint(10, "transport_tcp.receive count=%d" % count)
        f = ReceiveFilesFactory()
        try:
            mylistener = reactor.listenTCP(int(port), f)
        except:
            mylistener = None
            dhnio.DprintException()
        return mylistener

    def _loop(port, result, count):
        l = _try_receiving(port, count)
        if l is not None:
            dhnio.Dprint(8, "transport_tcp.receive started on port "+ str(port))
            result.callback(l)
            return
        if count > 10:
            dhnio.Dprint(1, "transport_tcp.receive WARNING port %s is busy!" % str(port))
            result.errback(None)
            return
        reactor.callLater(1, _loop, port, result, count+1)

    res = Deferred()
    _loop(port, res, 0)
    return res

#------------------------------------------------------------------------------

# In Putter "self.factory" references the parent object, so we can
# access arguments like "host", "port", and "filename"
class Putter(protocol.Protocol):
    fin = None
    sentBytes = 0
    def connectionMade(self):
        global _SendStatusFunc
        if not os.path.isfile(self.factory.filename):
            dhnio.Dprint(6, 'transport_tcp.Putter.connectionMade WARNING file %s was not found but we get connected to the %s' % (self.factory.filename, self.factory.host))
            if self.factory.do_status_report:
                _SendStatusFunc(
                    self.transport.getPeer(),
                    self.factory.filename,
                    'failed',
                    'tcp',
                    None,
                    'file was not found')
            self.transport.loseConnection()
            if self.factory.d is not None:
                if not self.factory.d.called:
                    self.factory.d.errback('failed')
            return

        try:
            self.fin = open(self.factory.filename, 'rb')
        except:
            dhnio.DprintException()
            if self.factory.do_status_report:
                _SendStatusFunc(
                    self.transport.getPeer(),
                    self.factory.filename,
                    'failed',
                    'tcp',
                    None,
                    'error opening file')
            self.transport.loseConnection()
            if self.factory.d is not None:
                if not self.factory.d.called:
                    self.factory.d.errback('failed')
            return

        fs = basic.FileSender()
        d = fs.beginFileTransfer(self.fin, self.transport, self.transformData)
        d.addCallback(self.finishedTransfer)
        d.addErrback(self.transferFailed)

    def transformData(self, data):
        self.sentBytes += len(data)
        #dhnio.Dprint(12, 'transport_tcp.Putter.transformData %d bytes sent' % self.sentBytes)
        return data

    def finishedTransfer(self, result):
        global _SendStatusFunc
        try:
            self.fin.close()
        except:
            dhnio.Dprint(1, 'transport_tcp.Putter.finishedTransfer ERROR close file failed')

        if self.factory.do_status_report:
            _SendStatusFunc(
                self.transport.getPeer(),
                self.factory.filename,
                'finished',
                'tcp')
        self.transport.loseConnection()
        if self.factory.d is not None:
            if not self.factory.d.called:
                self.factory.d.callback('finished')

    def transferFailed(self, err):
        global _SendStatusFunc
        dhnio.Dprint(1, 'transport_tcp.Putter.transferFailed NETERROR host=' + self.factory.host + " file=" + self.factory.filename)
        try:
            self.fin.close()
            dhnio.Dprint (14, 'transport_tcp.Putter.transferFailed - close file')
        except:
            dhnio.Dprint (1, 'transport_tcp.Putter.transferFailed ERROR closing file')

        if self.factory.do_status_report:
            _SendStatusFunc(
                self.transport.getPeer(),
                self.factory.filename,
                'failed',
                'tcp',
                err,
                'transfer failed')
                # not so good

        self.transport.loseConnection()
        if self.factory.d is not None:
            if not self.factory.d.called:
                self.factory.d.errback('failed')

    def connectionLost(self, reason):
        self.transport.loseConnection()
        try:
            self.fin.close()
        except:
            pass

class SendingFactory(ClientFactory):
    def __init__(self, filename, host, port, d = None, do_status_report=True):
        self.filename = filename
        self.host = host
        self.port = port
        self.protocol = Putter
        self.do_status_report = do_status_report
        self.d = d

    def clientConnectionFailed(self, connector, reason):
        global _SendStatusFunc
        ClientFactory.clientConnectionFailed(self, connector, reason)
        if self.do_status_report:
            _SendStatusFunc(
                connector.getDestination(),
                self.filename,
                'failed',
                'tcp',
                reason,
                'connection failed')
        if self.d is not None:
            if not self.d.called:
                self.d.errback('failed')
        name = str(reason.type.__name__)
        dhnio.Dprint(10, 'transport_tcp.clientConnectionFailed NETERROR [%s] with %s:%s' % (
            name,
            connector.getDestination().host,
            connector.getDestination().port,))

#------------------------------------------------------------------------------

class ReceiveFiles(protocol.Protocol):
    filename = ""     # string with path/filename
    fd = ""           # integer file descriptor like os.open() returns
    peer = ""
    def connectionMade(self):
        if self.peer == "":
            self.peer = self.transport.getPeer()
        else:
            if self.peer != self.transport.getPeer():
                dhnio.Dprint(1, "transport_tcp.ReceiveFiles.connectionMade NETERROR thought we had one object per connection")

        if self.filename == "":
            self.fd, self.filename = tmpfile.make("tcp-in")
        else:
            raise Exception("transport_tcp.ReceiveFiles has second connection in same object")

    def dataReceived(self, data):
        amount = len(data)
        os.write(self.fd, data)

    def connectionLost(self, reason):
        global _ReceiveStatusFunc
        os.close(self.fd)
        _ReceiveStatusFunc(
            self.filename,
            "finished",
            'tcp',
            self.transport.getPeer(),
            reason)


class ReceiveFilesFactory(ServerFactory):
    def buildProtocol(self, addr):
        p = ReceiveFiles()
        p.factory = self
        return p

#------------------------------------------------------------------------------

def SendStatusFuncDefault(host, filename, status, proto='', error=None, message=''):
    try:
        #import transport_control
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


_SendStatusFunc = SendStatusFuncDefault
_ReceiveStatusFunc = ReceiveStatusFuncDefault


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

if __name__ == "__main__":
    #import datahaven.p2p.memdebug as memdebug
    #memdebug.start(8080)
    dhnio.SetDebug(20)
    dhnio.LifeBegins()

    if len(sys.argv) == 2:
        r = receive(sys.argv[1])
        reactor.run()
    elif len(sys.argv) == 4:
        send(sys.argv[3], sys.argv[1], sys.argv[2])
        reactor.run()
    elif len(sys.argv) == 5:
        l = task.LoopingCall(send, sys.argv[3], sys.argv[1], sys.argv[2])
        l.start(float(sys.argv[4]))
        reactor.run()
    else:
        usage()

