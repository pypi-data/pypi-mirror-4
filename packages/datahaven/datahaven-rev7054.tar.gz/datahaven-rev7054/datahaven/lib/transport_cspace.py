#!/usr/bin/python
#transport_cspace.py
#
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2012
#    Use of this software constitutes acceptance of the Terms of Use
#      http://datahaven.net/terms_of_use.html
#    All rights reserved.
#
#

DEBUG = True
MEMDEBUG = False

import os
import sys
import threading
import imp
import time
import socket
from struct import pack, unpack
import threading


if __name__ == '__main__':
    sys.path.insert(0, os.path.abspath('..'))
    #dirpath = os.path.dirname(os.path.abspath(__file__))
    #sys.path.insert(0, os.path.abspath(os.path.join(dirpath, '..')))
    import dhnio
    dhnio.SetDebug(20)


try:
    from twisted.internet import reactor
except:
    sys.exit('Error initializing twisted.internet.reactor in transport_cspace.py')


from zope.interface import implements
from twisted.internet import interfaces
from twisted.internet.defer import Deferred, succeed


import misc
import dhnio
import settings
import tmpfile
import contacts



NEW_USER_PASSWORD_LENGTH = 12

_EventQueue = []
_EventQueuePoolDelay = 0.2
_Status = ''
_StatusNotifyFunc = None
_ContactStatusNotifyFunc = None
_SendStatusReportFunc = None
_ReceiveStatusReportFunc = None

_State = ''
_Listener = None
_ShutdownCalled = False
_ShutdownTriggerID = None

#------------------------------------------------------------------------------

class DummyClass:
    pass

def DummyDecorator(x):
    def y(z):
        pass
    return y

def hackImport():
    sys.modules['cspace.main.incomingprompt'] = imp.new_module('cspace.main.incomingprompt')
    sys.modules['cspace.main.incomingprompt'].IncomingPromptWindow = DummyClass

    sys.modules['cspace.main.dialogs'] = imp.new_module('cspace.main.dialogs')
    sys.modules['cspace.main.dialogs'].CreateKeyDialog = DummyClass
    sys.modules['cspace.main.dialogs'].CreateKeyDoneDialog = DummyClass
    sys.modules['cspace.main.dialogs'].GoOnlineDialog = DummyClass
    sys.modules['cspace.main.dialogs'].KeyInfoDialog = DummyClass
    sys.modules['cspace.main.dialogs'].AddContactDialog = DummyClass
    sys.modules['cspace.main.dialogs'].ContactInfoDialog = DummyClass
    sys.modules['cspace.main.dialogs'].PermissionsDialog = DummyClass
    sys.modules['cspace.main.dialogs'].UpdateNotifyWindow = DummyClass

    sys.modules['cspace.main.ui'] = imp.new_module('cspace.main.ui')
    sys.modules['cspace.main.ui.Ui_MainWindow'] = imp.new_module('cspace.main.ui.Ui_MainWindow')
    sys.modules['cspace.main.ui.Ui_MainWindow'].Ui_MainWindow = DummyClass

    sys.modules['cspace.main.ui.images_rc'] = imp.new_module('cspace.main.ui.images_rc')

    sys.modules['nitro.qt4reactor'] = imp.new_module('nitro.qt4reactor')
    sys.modules['nitro.qt4reactor'].Qt4Reactor = DummyClass

    sys.modules['PyQt4'] = imp.new_module('PyQt4')
    sys.modules['PyQt4.QtCore'] = imp.new_module('PyQt4.QtCore')
    sys.modules['PyQt4'].QtCore = sys.modules['PyQt4.QtCore']
    sys.modules['PyQt4.QtGui'] = imp.new_module('PyQt4.QtGui')
    sys.modules['PyQt4'].QtGui = sys.modules['PyQt4.QtGui']

    sys.modules['PyQt4.QtCore'].pyqtSignature = DummyDecorator
    sys.modules['PyQt4.QtCore'].QSize = DummyClass
    sys.modules['PyQt4.QtCore'].SIGNAL = 0

    sys.modules['PyQt4.QtGui'].QApplication = DummyClass
    sys.modules['PyQt4.QtGui'].qApp = DummyClass
    sys.modules['PyQt4.QtGui'].QMessageBox = DummyClass
    sys.modules['PyQt4.QtGui'].QIcon = DummyClass
    sys.modules['PyQt4.QtGui'].QMainWindow = DummyClass
    sys.modules['PyQt4.QtGui'].QDialog = DummyClass
    sys.modules['PyQt4.QtGui'].QListWidgetItem = DummyClass
    sys.modules['PyQt4.QtGui'].QMenu = DummyClass
    sys.modules['PyQt4.QtGui'].QAction = DummyClass
    sys.modules['PyQt4.QtGui'].QPixmap = DummyClass

def addrToStrFixed( addr ) :
    ip = unpack( 'I', socket.inet_aton(addr[0]) )[0]
    port = addr[1]
    return pack( '!IH', ip, port )

def fix_addrToStr_bug():
    sys.modules['cspace.dht.util'].addrToStr = addrToStrFixed

#class mysocket(socket._socketobject):
#    def __init__(self, family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0, _sock=None):
#        print 'mysocket.__init__', family, type, proto, _sock
#        socket._socketobject.__init__(self, family, type, proto, _sock)
#        print '_sock is', self._sock
#
#    def __del__(self):
#        print 'mysocket.__del__'
#        #socket._socketobject.__del__(self)
#
#    def close(self, _closedsocket=socket._closedsocket,
#              _delegate_methods=socket._delegate_methods, setattr=setattr):
#        print 'mysocket.close', self._sock
#        socket._socketobject.close(self, _closedsocket, _delegate_methods, setattr)

#def hack_sockets():
#    sys.modules['socket'].socket = mysocket

#_ImportDone = False
#if not _ImportDone:
    #_ImportDone = True
    #hackImport()
    #import cspace_application
    #hackNCrypt()
    #fix_addrToStr_bug()
    #hack_sockets()

import cspace_application


#------------------------------------------------------------------------------

def run(init_cb=None):
    def init_callback(status):
        global _State
        dhnio.Dprint(4, 'transport_cspace.run.init_callback status=%s init_cb=%s thread is %s' % (
            status, str(init_cb), threading.currentThread().getName()))
        oldState = _State
        _State = status
        dhnio.Dprint(4, 'transport_cspace.run.init_callback State: [%s]->[%s]' % (oldState, _State))
        if init_cb is not None:
            reactor.callFromThread(init_cb, status)
    try:
        dhnio.Dprint(4, 'transport_cspace.run starting')
        #-- START CSPACE  HERE ---------------------------------------------------------
        cspace_application.run(init_callback)
        #------------------------------------------------------------------------------
        dhnio.Dprint(4, 'transport_cspace.run finished')
    except:
        dhnio.Dprint(4, 'transport_cspace.run ERROR')
        dhnio.DprintException()


def init(_resultDefer=None):
    global _State
    if _State != '':
        dhnio.Dprint(2, 'transport_cspace.init WARNING already called and current _State is '+_State)
        return succeed(_State)
    dhnio.Dprint(4, 'transport_cspace.init')

    _State = 'init'
    init_started = time.time()
    resultDefer = _resultDefer
    if resultDefer is None:
        resultDefer = Deferred()

    def waiting():
        global _State
        if time.time() - init_started > 60*2:
            dhnio.Dprint(4, 'transport_cspace.init.waiting will fire [%s] in errback' % _State)
            _State = 'timeout'
            resultDefer.errback(_State)
            return
        if _State == 'online':
            dhnio.Dprint(4, 'transport_cspace.init.waiting will fire [%s] in callback' % _State)
            resultDefer.callback(_State)
            return
        if _State == 'offline':
            dhnio.Dprint(4, 'transport_cspace.init.waiting will fire [%s] in errback' % _State)
            resultDefer.errback(_State)
            return
        reactor.callLater(0.1, waiting)

    def do_init():
        global _ShutdownTriggerID
        keyID = cspace_application.getKeyID()
        dhnio.Dprint(4, 'transport_cspace.init.do_init keyID='+keyID)

        if settings.getCSpaceKeyID() != keyID:
            dhnio.Dprint(4, 'transport_cspace.init.do_init will update user settings KeyID='+keyID)
            settings.setCSpaceKeyID(keyID)

        _ShutdownTriggerID = reactor.addSystemEventTrigger('before', 'shutdown', shutdown)

        dhnio.Dprint(4, 'transport_cspace.init.do_init will start cspace in a new thread')
        #reactor.callInThread(run, status_callback)
        reactor.callInThread(run)

    def new_key_done(x):
        dhnio.Dprint(4, 'transport_cspace.init.new_key_done: ' + str(x))
        reactor.callLater(0, do_init)

    def new_key_failed(x, resultDefer):
        dhnio.Dprint(4, 'transport_cspace.init.new_key_failed: ' + str(x))
        resultDefer.errback('not installed')

    config()

    process_events()

    waiting()

    if not cspace_application.isInstalled():
        dhnio.Dprint(4, 'transport_cspace.init want to register new key')
        d = install()
        d.addCallback(new_key_done)
        d.addErrback(new_key_failed, resultDefer)
        return resultDefer

    do_init()

    return resultDefer


def shutdown():
    global _ShutdownCalled
    if _ShutdownCalled:
        #dhnio.Dprint(2, 'transport_cspace.shutdown WARNING already called')
        return succeed('already called')
    _ShutdownCalled = True
    dhnio.Dprint(4, 'transport_cspace.shutdown')
    result = Deferred()

    def done(x):
        dhnio.Dprint(4, 'transport_cspace.shutdown.done: ' + str(x))
        global _State
        global _ShutdownCalled
        global _ShutdownTriggerID
        _State = ''
        _ShutdownCalled = False
        reactor.removeSystemEventTrigger(_ShutdownTriggerID)
        result.callback(x)

    cspace_application.stop(done)
    _State = 'shutdown'
    return result


def config():
    try:
        cspace_application.setSendNotifyFunc(onSent)
        cspace_application.setReceiveNotifyFunc(onReceive)
        cspace_application.setStatusNotifyFunc(onStatus)
        cspace_application.setContactStatusNotifyFunc(onContactStatus)

        cspace_application.setTempLocation(tmpfile.subdir('cspace-in'))

        cspace_application.hackConfigDir(getDHNConfigDir)
        cspace_application.hackPermissions()

        cspace_application._stdOutFunc = cspaceDprint
        if misc.getLocalID() == settings.CentralID():
            logLevel = 0
        else:
            logLevel = 50 - dhnio.DebugLevel * 8
            if logLevel < 0:
                logLevel = 0
        cspace_application.init_log(logLevel, settings.CSpaceLogFilename())

    except:
        dhnio.Dprint(2, 'transport_cspace.config ERROR during configuration')
        dhnio.DprintException()


def cspaceDprint(s):
    dhnio.Dprint(6, '      ' + s.strip())

#------------------------------------------------------------------------------

def push_event(e, data):
    global _EventQueue
    _EventQueue.append((e, data))

def pop_event():
    global _EventQueue
    try:
        e, d = _EventQueue.pop(0)
        
        if DEBUG:
            dhnio.Dprint(14, 'transport_cspace.process_events [%s] %s' % (e, d)) 

        if e == 'sent':
            if _SendStatusReportFunc is not None:
                _SendStatusReportFunc(d[0], d[1], d[2], d[3], d[4], d[5])

        elif e == 'received':
            tmpfile.register(d[0])
            if _ReceiveStatusReportFunc is not None:
                _ReceiveStatusReportFunc(d[0], d[1], d[2], d[3], d[4], d[5])

        elif e == 'status':
            if _StatusNotifyFunc is not None:
                _StatusNotifyFunc(d)

        elif e == 'contact-status':
            if _ContactStatusNotifyFunc is not None:
                _ContactStatusNotifyFunc(d[0], d[1])

    except:
        dhnio.DprintException()

def process_events():
    global _EventQueue
    global _EventQueuePoolDelay
    global _StatusNotifyFunc
    global _ContactStatusNotifyFunc
    global _SendStatusReportFunc
    global _ReceiveStatusReportFunc
    
    if len(_EventQueue) > 0:
        pop_event()
        _EventQueuePoolDelay = 0.01
    else:
        if _EventQueuePoolDelay < 2.0:
            _EventQueuePoolDelay *= 2.0

    # attenuation
    reactor.callLater(_EventQueuePoolDelay, process_events)

#------------------------------------------------------------------------------

def onSent(host, filename, status, proto='', error=None, message=''):
    push_event('sent', (host, filename, status, proto, error, message))


def onReceive(filename, status, proto='', host=None, error=None, message=''):
    push_event('received', (filename, status, proto, host, error, message))


def onStatus(status):
    global _Status
    if _Status != status:
        dhnio.Dprint(12, 'transport_cspace.onStatus [%s]->[%s]' % (_Status, status))
        _Status = status
        push_event('status', status)


def onContactStatus(keyid, status):
    push_event('contact-status', (keyid, status))


#------------------------------------------------------------------------------


def register(username):
    dhnio.Dprint(4, 'transport_cspace.register ' + username)
    result = Deferred()
    cspace_application.register(username)
    return succeed('registered')


def send(keyID, filename):
    #dhnio.Dprint(12, 'transport_cspace.send %s %s' % (keyID, os.path.basename(filename)))
    cspace_application.send(keyID, filename)


def receive():
    dhnio.Dprint(6, 'transport_cspace.receive')
    return succeed('ready')


def add(keyID):
    dhnio.Dprint(6, 'transport_cspace.add ' + keyID)
    resultDefer = Deferred()
    def done(c):
        if c is None:
            dhnio.Dprint(6, 'transport_cspace.add.done ERROR adding ' + keyID)
            resultDefer.errback(c)
        else:
            dhnio.Dprint(6, 'transport_cspace.add.done keyID=%s contact.name=%s' %(keyID, c.name))
            resultDefer.callback(c)
        return c
    cspace_application.add(keyID, done)
    return resultDefer


def isContact(keyID):
    return cspace_application.isContact(keyID)


def state(keyID):
    return cspace_application.state(keyID)


def status(keyID):
    return cspace_application.status(keyID)


def my_state():
    global _State
    return _State


def go_online():
    dhnio.Dprint(6, 'transport_cspace.go_online')
    return cspace_application.online()


def go_offline():
    dhnio.Dprint(6, 'transport_cspace.go_offline')
    return cspace_application.offline()


def receiving_streams(keyID):
    return cspace_application.receiving_streams(keyID)


def sending_streams(keyID):
    return cspace_application.sending_streams(keyID)


def probe(keyID):
    dhnio.Dprint(6, 'transport_cspace.probe ' + keyID)
    resultDefer = Deferred()
    def done(contact, status):
        dhnio.Dprint(6, 'transport_cspace.probe.done %s is [%s]' % (keyID, status))
        resultDefer.callback(status)
        return status
    cspace_application.probe(keyID, done)
    return resultDefer


def install(username='', password=''):
    result = Deferred()
    def done(keyID):
        dhnio.Dprint(4, 'transport_cspace.install.done keyID=' + str(keyID))
        if keyID < 0:
            result.errback(returnCode)
        else:
            result.callback(keyID)
    if username == '':
        username = misc.getIDName()
    if password == '':
        password = misc.rndstr(NEW_USER_PASSWORD_LENGTH)
    username = username.replace('-', '_')
    username = 'dhn_' + username
    dhnio.Dprint(4, 'transport_cspace.install username=' + username)
    reactor.callInThread(cspace_application.install, username, password, done)
    #cspace_application.install(username, password, done, failed)
    return result

#------------------------------------------------------------------------------

class PseudoListener:
    implements(interfaces.IListeningPort)
    def startListening(self):
        global _State
        dhnio.Dprint(4, 'transport_cspace.startListening in state ' + str(_State))
        if _State == '':
            return init()
        cspace_application.online()
        return succeed(_State)

    def stopListening(self):
        global _State
        dhnio.Dprint(4, 'transport_cspace.stopListening in state ' + str(_State))
        #return shutdown()
        cspace_application.offline()
        return succeed('offline')

    def getHost(self):
        return str(cspace_application.getKeyID())


def getListener():
    global _Listener
    if _Listener is None:
        _Listener = PseudoListener()
    return _Listener

#------------------------------------------------------------------------------

def getKeyID():
    return cspace_application.getKeyID()


def getDHNConfigDir(name):
    newDir = os.path.join(settings.BaseDir(), name.lower())
    dhnio.Dprint(6, 'transport_cspace.getDHNConfigDir [%s]=[%s]' % (name, newDir))
    return newDir

#------------------------------------------------------------------------------

def close_not_needed_streams():
    list_cspace_contacts = []
    list_streams_to_close = []
    for idurl in contacts.getContactsAndCorrespondents():
        ident = contacts.getContact(idurl)
        if ident is None:
            continue
        cspace_contact = ident.getProtoContact('cspace')
        if cspace_contact is None:
            continue
        list_cspace_contacts.append(cspace_contact[9:])
    for keyID, streams in cspace_application._SendingStreams.items():
        if keyID in list_cspace_contacts:
            continue
        for stream in streams:
            list_streams_to_close.append((stream, keyID, 'sending'))
    for keyID, streams in cspace_application._ReceivingStreams.items():
        if keyID in list_cspace_contacts:
            continue
        for stream in streams:
            list_streams_to_close.append((stream, keyID, 'receiving'))
    for stream, keyID, direction in list_streams_to_close:
        dhnio.Dprint(8, 'transport_cspace.close_not_needed_streams want to close %s stream for [%s]' % (direction, keyID))
        stream.close_stream()
    del list_cspace_contacts
    del list_streams_to_close

def SetOpenedSendingStreamsNumber(num):
    cspace_application.OPENED_SENDING_STREAMS_NUMBER = num

def SetOpenedReceivingStreamsNumber(num):
    cspace_application.OPENED_RECEIVING_STREAMS_NUMBER = num

#------------------------------------------------------------------------------

def SetStatusNotifyFunc(f):
    global _StatusNotifyFunc
    _StatusNotifyFunc = f

def SetContactStatusNotifyFunc(f):
    global _ContactStatusNotifyFunc
    _ContactStatusNotifyFunc = f

def SetSendStatusReportFunc(f):
    global _SendStatusReportFunc
    _SendStatusReportFunc = f

def SetReceiveStatusReportFunc(f):
    global _ReceiveStatusReportFunc
    _ReceiveStatusReportFunc = f

#if __name__ == '__main__':
#    def DefaultSendStatusReportFunc(a,b,c,d,e,f):
#        print 'send', a,b,c,d,e,f
#    def DefaultReceiveStatusReportFunc(a,b,c,d,e,f):
#        print 'recv', a,b,c,d,e,f
#    _SendStatusReportFunc = DefaultSendStatusReportFunc
#    _ReceiveStatusReportFunc = DefaultReceiveStatusReportFunc

#------------------------------------------------------------------------------


def test_init_done(x):
    print 'test_init_done', x
    print 'my key id is', cspace_application.getKeyID()
#    if misc.getIDName() == 'veeesel':
#        reactor.callLater(15, send, '149904', 'cspacetest.log ')
    if misc.getIDName() == 'veselin':
        reactor.callLater(15, send, '149905', sys.argv[1])
    #reactor.callLater(5, shutdown)
    return x


def usage():
    print '''
usage:
    transport_cspace.py send <keyID> <filename>
    transport_cspace.py receive
    transport_cspace.py install <username> <password>
    transport_cspace.py add <keyID>
'''


def test():
##    from cspace.dht.util import verifySignature, computeSignature
##    settings.init()
##    dhnio.SetDebug(20)
##    config()
##    p = cspace_application.profile()
##    data = open('buf/data', 'rb').read()
##    signature = open('buf/signature', 'rb').read()
##    updateLevel = int(open('buf/updateLevel', 'rb').read())
##    contact = p.getContactByName(sys.argv[2])
##    verifySignature(contact.publicKey, data, updateLevel, signature)
    cspace_application.test()


def main(argv=sys.argv):

    dhnio.LifeBegins()
    
    if argv.count('send'):
        keyID = argv[2]
        filename = argv[3]
        def DoSend(x):
            dhnio.Dprint(4, 'DoSend ' + str(x))
#            if x == 'offline':
#                reactor.stop()
#                os._exit(x)
#                return
            reactor.callLater(0, send, keyID, filename)
            reactor.callLater(10, DoSend, 0)
        def InitDone(x):
            dhnio.Dprint(4, 'InitDone [%s]' % str(x))
            if not isContact(keyID):
                add(keyID).addCallback(lambda x: probe(keyID).addCallback(DoSend))
            else:
                probe(keyID).addCallback(DoSend)
        def DoInit():
            init().addBoth(DoSend)
        settings.init()
        dhnio.SetDebug(16)
        reactor.callLater(0, DoInit)
        if MEMDEBUG:
            try:
                import memdebug
                memdebug.start(9993)
                reactor.addSystemEventTrigger('before', 'shutdown', memdebug.stop)
            except:
                pass
        reactor.run()

    elif argv.count('receive'):
        def ReceivingStarted(x):
            dhnio.Dprint(4, 'ReceivingStarted state=' + str(x))
            #reactor.callLater(3, reactor.stop)
            #print 'threads', threading.enumerate()
        settings.init()
        dhnio.SetDebug(16)
        init().addBoth(ReceivingStarted)
        if MEMDEBUG:
            try:
                import memdebug
                memdebug.start(9993)
                reactor.addSystemEventTrigger('before', 'shutdown', memdebug.stop)
            except:
                pass
        reactor.run()

    elif argv.count('install'):
        settings.init()
        dhnio.SetDebug(20)
        config()
        username = ''
        if len(argv) >= 2:
            username = argv[2]
        password = ''
        if len(argv) >= 3:
            password = argv[3]
        install(username, password)

    elif argv.count('add'):
        settings.init()
        dhnio.SetDebug(20)
        def added(x):
            dhnio.Dprint(4, 'ADDED: ' + str(x))
            reactor.stop()
            dhnio.Dprint(4, 'EXIT NOW')
            #os._exit(0)
        def doAdd(x):
            add(argv[2]).addBoth(added)
        d = init()
        d.addCallback(doAdd)
        d.addErrback(lambda x: reactor.stop())
        if MEMDEBUG:
            try:
                import memdebug
                memdebug.start(9993)
                reactor.addSystemEventTrigger('before', 'shutdown', memdebug.stop)
            except:
                pass
        reactor.run()

    elif argv.count('test'):
        test()

    else:
        usage()
        return 0

    return 0


if __name__ == '__main__':
    print 'starting', threading.enumerate()
    ret = main()
    print 'EXIT ret =', ret
    print 'finishing', threading.enumerate()
    #os._exit(ret)




