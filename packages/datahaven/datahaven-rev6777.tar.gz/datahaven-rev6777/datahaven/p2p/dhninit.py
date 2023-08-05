#!/usr/bin/python
#dhninit.py
#
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2012
#    All rights reserved.
#

import os
import sys
import time

try:
    from twisted.internet import reactor
except:
    sys.exit('Error initializing twisted.internet.reactor in dhninit.py')
from twisted.internet.defer import Deferred,  DeferredList
from twisted.internet import task

import lib.dhnio as dhnio


# need to change directory in case we were not in the p2p directory when datahaven started up,
# need it to find dhntester.py and potentially others
#try:
#    os.chdir(os.path.abspath(os.path.dirname(__file__)))
#except:
#    pass

UImode = ''

#------------------------------------------------------------------------------

def run(UI='', options=None, args=None, overDict=None):
    init(UI, options, args, overDict)


def init_local(UI=''):
    global UImode
    UImode = UI
    dhnio.Dprint(2, "dhninit.init_local")

    import lib.settings as settings
    import lib.misc as misc
    misc.init()
    misc.UpdateSettings()

    #Here we can change users settings depending on user name
    #Small hack, but we want to do only during testing period.
    settings_patch()

    import lib.commands as commands
    commands.init()

    if sys.argv.count('--twisted'):
        class MyTwistedOutputLog:
            softspace = 0
            def read(self): pass
            def write(self, s):
                dhnio.Dprint(0, s.strip())
            def flush(self): pass
            def close(self): pass
        from twisted.python import log as twisted_log
        twisted_log.startLogging(MyTwistedOutputLog(), setStdout=0)
#    import twisted.python.failure as twisted_failure
#    twisted_failure.startDebugMode()
#    twisted_log.defaultObserver.stop()

    from twisted.internet import defer
    defer.setDebugging(True)

    if settings.enableWebStream():
        misc.StartWebStream()

    if settings.enableWebTraffic():
        misc.StartWebTraffic()
        
    if settings.enableMemoryProfile():
        try:
            from guppy import hpy
            hp = hpy()
            hp.setrelheap()
            dhnio.Dprint(2, 'hp.heap():\n'+str(hp.heap()))
            dhnio.Dprint(2, 'hp.heap().byrcs:\n'+str(hp.heap().byrcs))
            dhnio.Dprint(2, 'hp.heap().byvia:\n'+str(hp.heap().byvia))
            import guppy.heapy.RM
        except:
            dhnio.Dprint(2, "dhninit.init_local guppy package is not installed")            

    import lib.tmpfile as tmpfile
    tmpfile.init(settings.getTempDir())

    import lib.dhnnet as dhnnet
    settings.update_proxy_settings()

    import run_upnpc
    run_upnpc.init()

    import lib.dhncrypto as dhncrypto
    import lib.identity as identity

    import webcontrol
    import lib.automats as automats
    webcontrol.GetGlobalState = automats.get_global_state

    import dhnupdate
    dhnupdate.SetNewVersionNotifyFunc(webcontrol.OnGlobalVersionReceived)

    start_logs_rotate()

def init_contacts(callback=None, errback=None):
    dhnio.Dprint(2, "dhninit.init_contacts")

    import lib.misc as misc
    misc.loadLocalIdentity()
    if misc._LocalIdentity is None:
        if errback is not None:
            errback(1)
        return

    import lib.contacts as contacts
    contacts.init()

    import lib.identitycache as identitycache
    identitycache.init(callback, errback)


def init_connection():
    global UImode
    dhnio.Dprint(2, "dhninit.init_connection")

    import webcontrol

    import contacts_status
    contacts_status.init()

    import central_service
    central_service.OnListSuppliersFunc = webcontrol.OnListSuppliers
    central_service.OnListCustomersFunc = webcontrol.OnListCustomers

    import customerservice
    customerservice.init()

    import money

    import message
    message.init()
    message.OnIncommingMessageFunc = webcontrol.OnIncommingMessage

    import lib.automats as automats
    automats.SetGlobalStateNotifyFunc(webcontrol.OnGlobalStateChanged)
    automats.SetSingleStateNotifyFunc(webcontrol.OnSingleStateChanged)

    import identitypropagate
    identitypropagate.init()

    try:
        from dhnicon import USE_TRAY_ICON
    except:
        USE_TRAY_ICON = False
        dhnio.DprintException()

    if USE_TRAY_ICON:
        import dhnicon
        dhnicon.SetControlFunc(webcontrol.OnTrayIconCommand)

    #init the mechanism for sending and requesting files for repairing backups
    import io_throttle
    io_throttle.init()

    import backup_db
    backup_db.init()

    import backups
    backups.init()
    backups.SetBackupStatusNotifyCallback(webcontrol.OnBackupStats)
    backups.SetLocalFilesNotifyCallback(webcontrol.OnReadLocalFiles)
    
    #backup_monitor.init()
    #backup_monitor.OnIncomingListFilesFunc = webcontrol.OnIncomingListFiles
    #backup_monitor.OnIncomingDataPacketFunc = webcontrol.OnIncomingDataPacket
    #backup_monitor.OnNewBackupListFilesFunc = webcontrol.OnNewBackupListFiles
    #backup_monitor.SetStatusCallBackForGuiBackup(webcontrol.OnBackupStatus)

    import restore_monitor
    restore_monitor.init()
    restore_monitor.OnRestorePacketFunc = webcontrol.OnRestoreProcess
    restore_monitor.OnRestoreDoneFunc = webcontrol.OnRestoreDone

#    import summary
#    summary.init()

#    webcontrol.ready()

#    if UImode.lower() == 'show':
#        wcinit.addCallback(webcontrol.show)
#        wcinit.addErrback(lambda x: dhnio.DprintException())


def init_modules():
    dhnio.Dprint(2,"dhninit.init_modules")

    import webcontrol

    import localtester
    import backupshedule
    #import ratings
    import fire_hire
    #import backup_monitor
    import dhnupdate

    #reactor.callLater(3, backup_monitor.start)

    reactor.callLater(5, localtester.init)

    reactor.callLater(10, backupshedule.init)

    #reactor.callLater(20, ratings.init)

    #reactor.callLater(25, firehire.init)

    reactor.callLater(15, dhnupdate.init)

    # finally we can decrease our priority
    # because during backup DHN eats too much CPU
    dhnio.LowerPriority()

    webcontrol.OnInitFinalDone()


def shutdown(x=None):
    global initdone
    dhnio.Dprint(2, "dhninit.shutdown " + str(x))
    dl = []

    import lib.stun
    dl.append(lib.stun.stopUDPListener())
#    import backup_monitor
#    backup_monitor.shutdown()
#    
#    import p2p_connector
#    p2p_connector.shutdown()

    import dobackup
    dobackup.shutdown()

    import backups
    backups.shutdown()

#    import fire_hire
#    fire_hire.shutdown()

    import ratings
    ratings.shutdown()

    import contacts_status
    contacts_status.shutdown()

    import run_upnpc
    run_upnpc.shutdown()

    import localtester
    localtester.shutdown()

    import webcontrol
    dl.append(webcontrol.shutdown())

    import lib.transport_control as transport_control
    dl.append(transport_control.shutdown())

    import lib.weblog as weblog
    weblog.shutdown()

    initdone = False

    return DeferredList(dl)


def shutdown_restart(param=''):
    dhnio.Dprint(2, "dhninit.shutdown_restart ")

    def do_restart(param):
        import lib.misc as misc
        misc.DoRestart(param)

    def shutdown_finished(x, param):
        dhnio.Dprint(2, "dhninit.shutdown_restart.shutdown_finished want to stop the reactor")
        reactor.addSystemEventTrigger('after','shutdown', do_restart, param)
        reactor.stop()

    d = shutdown('restart')
    d.addBoth(shutdown_finished, param)


def shutdown_exit(x=None):
    dhnio.Dprint(2, "dhninit.shutdown_exit ")

    def shutdown_reactor_stop(x=None):
        dhnio.Dprint(2, "dhninit.shutdown_exit want to stop the reactor")
        reactor.stop()

    d = shutdown(x)
    d.addBoth(shutdown_reactor_stop)


def settings_patch():
    dhnio.Dprint(6, 'dhninit.settings_patch ')
    #import lib.settings as settings
    #settings.enableCSpace(True)
    #settings.setUPNPatStartup(True)
    #settings.enableQ2Q(False)
    #settings.enableHTTP(False)
    #settings.enableHTTPServer(False)

#    import lib.misc as misc
#    settings.enableQ2Q(True)    #small hook to switch on the q2q

#    if not misc.getIDName() in ['dhncentral', 'petarpenev', 'veseleeypc', 'ekaterina', 'veselin']:
#        settings.enableQ2Q(False)

#I want to rename the icon name to DataHaven
#Because it is too long and looks ugly on 2 lines
#    misc.removeWindowsShortcut('DataHaven.Net.lnk')
#    misc.removeStartMenuShortcut('DataHaven.Net.lnk')
#    misc.removeWindowsShortcut('DataHaven.lnk')
#    misc.removeStartMenuShortcut('DataHaven.lnk')
#    misc.removeWindowsShortcut('Data Haven.lnk')
#    misc.removeStartMenuShortcut('Data Haven.lnk')
#    misc.removeWindowsShortcut('Data Haven Net.lnk')
#    misc.removeStartMenuShortcut('Data Haven Net.lnk')

#    if misc.getIDName() in ['nonsons', 'van4eg', 'kirill']:
#    settings.uconfig().set('transport.transport-q2q.transport-q2q-enable', 'True')
#    settings.uconfig().set('updates.updates-shedule', '4\n12:00:00\n1\n\n')

#    if settings.uconfig('transport.transport-q2q.transport-q2q-host') != 'datahaven.net':
#        settings.uconfig().set('transport.transport-q2q.transport-q2q-host', 'datahaven.net')
#        settings.uconfig().set('transport.transport-q2q.transport-q2q-username', '')
#        settings.uconfig().set('transport.transport-q2q.transport-q2q-password', '')

    #import lib.misc as misc
    #if misc.getLocalIdentity().getProtoContact('cspace') is None:
        #dhnio.Dprint(4, 'dhninit.settings_patch want to enable cspace')

        #import lib.transport_cspace as transport_cspace
        #reactor.callLater(60*2, transport_cspace.install)
#        def cspace_init_done(x):
#            dhnio.Dprint(4, 'dhninit.settings_patch cspace init was done')
#            def cspace_register_done(x):
#                dhnio.Dprint(4, 'dhninit.settings_patch cspace registration done')
#                settings.enableCSpace(True)
#                settings.uconfig().update()
#            transport_cspace.register(misc.getIDName()).addCallback(cspace_register_done)
#        transport_cspace.init().addCallback(cspace_init_done)
    import lib.settings as settings
    settings.enableUDP(True)
    settings.enableCSpace(False)
    

def start_logs_rotate():
    dhnio.Dprint(4, 'dhninit.start_logs_rotate')
    def erase_logs():
        dhnio.Dprint(4, 'dhninit.erase_logs ')
        import lib.settings as settings
        logs_dir = settings.LogsDir()
        total_sz = 0
        for filename in os.listdir(logs_dir):
            filepath = os.path.join(logs_dir, filename)
            if not filename.endswith('.log'):
                # this is not a log file - we did not create it - do nothing
                continue
            if filename.startswith('dhnmain-'):
                # remove "old version" files, now we have files started with "dhn-" 
                try:
                    os.remove(os.path.join(logs_dir, filename))
                    dhnio.Dprint(6, 'dhninit.erase_logs %s was deleted because it is old version' % filename)
                except:
                    dhnio.Dprint(1, 'dhninit.erase_logs ERROR can not remove ' + filename)
                continue
            # count the total size of the all log files
            try:
                file_size = os.path.getsize(os.path.join(logs_dir, filename))
            except:
                file_size = 0
            total_sz += file_size 
            # if the file is bigger than 2mb - erase it
            if file_size > 1024*1024*2:
                if os.access(filepath, os.W_OK):
                    try:
                        os.remove(filepath)
                        dhnio.Dprint(6, 'dhninit.erase_logs %s was deleted because it is too big' % filename)
                    except:
                        dhnio.Dprint(1, 'dhninit.erase_logs ERROR can not remove ' + filename)
            # if this is a file for every execution (started with "dhn-") ... 
            if filename.startswith('dhn-'):
                # we check if file is writable - so we can remove it
                if not os.access(filepath, os.W_OK):
                    continue
                # get its datetime
                try:
                    dtm = time.mktime(time.strptime(filename[4:-4],'%y%m%d%H%M%S'))
                except:
                    dhnio.DprintException()
                    continue          
                # we want to check if it is more than 10 days old ...
                if time.time() - dtm > 60*60*24*10: 
                    try:
                        os.remove(filepath)
                        dhnio.Dprint(6, 'dhninit.erase_logs %s was deleted because it is old' % filename)
                    except:
                        dhnio.Dprint(1, 'dhninit.erase_logs ERROR can not remove ' + filename)
                    continue
                # also we want to check if all those files are too big - 5 MB is enough
                if total_sz > 1024*1024*5:
                    try:
                        os.remove(filepath)
                        dhnio.Dprint(6, 'dhninit.erase_logs %s was deleted because log files is too big' % filename)
                    except:
                        dhnio.Dprint(1, 'dhninit.erase_logs ERROR can not remove ' + filename)
                    continue
                     
    task.LoopingCall(erase_logs).start(60*60*24)



def check_install():
    dhnio.Dprint(2, 'dhninit.check_install ')
    import lib.settings as settings
    import lib.identity as identity
    import lib.dhncrypto as dhncrypto

    keyfilename = settings.KeyFileName()
    idfilename = settings.LocalIdentityFilename()
    if not os.path.exists(keyfilename) or not os.path.exists(idfilename):
        dhnio.Dprint(2, 'dhninit.check_install local key or local id not exists')
        return False

    current_key = dhnio.ReadBinaryFile(keyfilename)
    current_id = dhnio.ReadBinaryFile(idfilename)

    if current_id == '':
        dhnio.Dprint(2, 'dhninit.check_install local identity is empty ')
        return False

    if current_key == '':
        dhnio.Dprint(2, 'dhninit.check_install private key is empty ')
        return False

    try:
        dhncrypto.InitMyKey()
    except:
        dhnio.Dprint(2, 'dhninit.check_install fail loading private key ')
        return False

    try:
        ident = identity.identity(xmlsrc=current_id)
    except:
        dhnio.Dprint(2, 'dhninit.check_install fail init local identity ')
        return False

    try:
        res = ident.Valid()
    except:
        dhnio.Dprint(2, 'dhninit.check_install wrong data in local identity   ')
        return False

    if not res:
        dhnio.Dprint(2, 'dhninit.check_install local identity is not valid ')
        return False

    dhnio.Dprint(2, 'dhninit.check_install done')
    return True


