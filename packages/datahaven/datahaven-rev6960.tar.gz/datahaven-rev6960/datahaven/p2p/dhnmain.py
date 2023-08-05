#!/usr/bin/python
#dhnmain.py
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

#-------------------------------------------------------------------------------

def show():
    import webcontrol
    webcontrol.show()
    return 0


def run(UI='', options=None, args=None, overDict=None):
    import lib.dhnio as dhnio
    dhnio.Dprint(6, 'dhnmai-n.run sys.path=%s' % str(sys.path))

    #---USE_TRAY_ICON---
    try:
        from dhnicon import USE_TRAY_ICON
        dhnio.Dprint(4, 'dhnmain.run USE_TRAY_ICON='+str(USE_TRAY_ICON))
        if dhnio.Linux() and not dhnio.X11_is_running():
            USE_TRAY_ICON = False
        if USE_TRAY_ICON:
            from twisted.internet import wxreactor
            wxreactor.install()
    except:
        USE_TRAY_ICON = False
        dhnio.DprintException()

    if USE_TRAY_ICON:
        if dhnio.Linux():
            icons_dict = {
                'red':      'icon-red-24x24.png',
                'green':    'icon-green-24x24.png',
                'gray':     'icon-gray-24x24.png',
                }
        else:
            icons_dict = {
                'red':      'icon-red.png',
                'green':    'icon-green.png',
                'gray':     'icon-gray.png',
                }
        import dhnicon
        icons_path = str(os.path.abspath(os.path.join(dhnio.getExecutableDir(), 'icons')))
        dhnio.Dprint(4, 'dhnmain.run call dhnicon.init(%s)' % icons_path)
        dhnicon.init(icons_path, icons_dict)
        def _tray_control_func(cmd):
            if cmd == 'exit':
                #import dhninit
                #dhninit.shutdown_exit()
                import shutdowner
                shutdowner.A('stop', ('exit', ''))
        dhnicon.SetControlFunc(_tray_control_func)

    dhnio.Dprint(4, 'dhnmain.run want to import twisted.internet.reactor')
    try:
        from twisted.internet import reactor
    except:
        dhnio.DprintException()
        sys.exit('Error initializing reactor in dhnmain.py\n')

    #---settings---
    import lib.settings as settings
    if overDict:
        settings.override_dict(overDict)
    settings.init()
    if not options or options.debug is None:
        dhnio.SetDebug(settings.getDebugLevel())

    #---logfile----
    if dhnio.EnableLog and dhnio.LogFile is not None:
        dhnio.Dprint(2, 'dhnmain.run want to switch log files')
        if dhnio.Windows() and dhnio.isFrozen():
            dhnio.StdOutRedirectingStop()
        dhnio.CloseLogFile()
        dhnio.OpenLogFile(settings.MainLogFilename()+'-'+time.strftime('%y%m%d%H%M%S')+'.log')
        if dhnio.Windows() and dhnio.isFrozen():
            dhnio.StdOutRedirectingStart()
            
    #---memdebug---
    if settings.uconfig('logs.memdebug-enable') == 'True':
        try:
            import lib.memdebug as memdebug
            memdebug_port = int(settings.uconfig('logs.memdebug-port'))
            memdebug.start(memdebug_port)
            reactor.addSystemEventTrigger('before', 'shutdown', memdebug.stop)
            dhnio.Dprint(2, 'dhnmain.run memdebug web server started on port %d' % memdebug_port)
        except:
            dhnio.DprintException()    

    dhnio.Dprint(2,"dhnmain.run UI=[%s]" % UI)

    if dhnio.Debug(10):
        dhnio.Dprint(0, '\n' + dhnio.osinfofull())

    dhnio.Dprint(4, 'dhnmain.run want to start automats')

    #---START!---
    import lib.automats as automats
    import initializer
    import shutdowner
    
    #reactor.callLater(0, initializer.A, 'run', UI)
    initializer.A('run', UI)

    #reactor.addSystemEventTrigger('before', 'shutdown', lambda : initializer.A('reactor-stopped'))

    dhnio.Dprint(2, 'dhnmain.run calling reactor.run()')
    reactor.run()
    dhnio.Dprint(2, 'dhnmain.run reactor stopped')
    # this will call initializer() without reactor.callLater(0, ... )
    # we do not have any timers initializer() so do not worry
    #initializer.A('reactor-stopped', use_reactor = False)
    shutdowner.A('reactor-stopped')

    dhnio.Dprint(2, 'dhnmain.run finished, EXIT')

    automats.get_automats_by_index().clear()

##    import threading
##    dhnio.Dprint(0, 'threads:')
##    for t in threading.enumerate():
##        dhnio.Dprint(0, '  '+str(t))

    dhnio.CloseLogFile()

    if dhnio.Windows() and dhnio.isFrozen():
        dhnio.StdOutRedirectingStop()

    return 0

#------------------------------------------------------------------------------

def parser():
    from optparse import OptionParser, OptionGroup
    parser = OptionParser(usage = usage())
    group = OptionGroup(parser, "Log")
    group.add_option('-d', '--debug',
                        dest='debug',
                        type='int',
                        help='set debug level',)
    group.add_option('-q', '--quite',
                        dest='quite',
                        action='store_true',
                        help='quite mode, do not print any messages to stdout',)
    group.add_option('-v', '--verbose',
                        dest='verbose',
                        action='store_true',
                        help='verbose mode, print more messages',)
    group.add_option('-n', '--no-logs',
                        dest='no_logs',
                        action='store_true',
                        help='do not use logs',)
    group.add_option('-o', '--output',
                        dest='output',
                        type='string',
                        help='print log messages to the file',)
    group.add_option('-t', '--tempdir',
                        dest='tempdir',
                        type='string',
                        help='set location for temporary files, default is ~/.datahaven/temp',)
    group.add_option('--twisted',
                        dest='twisted',
                        action='store_true',
                        help='show twisted log messages too',)
    group.add_option('--memdebug',
                        dest='memdebug',
                        action='store_true',
                        help='start web server to debug memory usage, need cherrypy and dozer modules',)
    parser.add_option_group(group)


    group = OptionGroup(parser, "Network")
    group.add_option('--tcp-port',
                        dest='tcp_port',
                        type='int',
                        help='set tcp port number for incoming connections',)
    group.add_option('--no-upnp',
                        dest='no_upnp',
                        action='store_true',
                        help='do not use UPnP',)
    group.add_option('--no-cspace',
                        dest='no_cspace',
                        action='store_true',
                        help='do not use transport_cspace',)
    group.add_option('--memdebug-port',
                        dest='memdebug_port',
                        type='int',
                        default=9996,
                        help='set port number for memdebug web server, default is 9995',)    
    parser.add_option_group(group)

    return parser


def override_options(opts, args):
    overDict = {}
    if opts.tcp_port:
        overDict['transport.transport-tcp.transport-tcp-port'] = str(opts.tcp_port)
    if opts.no_upnp:
        overDict['other.upnp-enabled'] = 'False'
    #if opts.no_q2q:
        #overDict['transport.transport-q2q.transport-q2q-enable'] = 'False'
    if opts.no_cspace:
        overDict['transport.transport-cspace.transport-cspace-enable'] = 'False'
    if opts.tempdir:
        overDict['folder.folder-temp'] = opts.tempdir
    if opts.debug or str(opts.debug) == '0':
        overDict['logs.debug-level'] = str(opts.debug)
    if opts.memdebug:
        overDict['logs.memdebug-enable'] = str(opts.memdebug)
        if opts.memdebug_port:
            overDict['logs.memdebug-port'] = str(opts.memdebug_port)
        else:
            overDict['logs.memdebug-port'] = '9996'
    return overDict

#------------------------------------------------------------------------------ 

def kill():
    import lib.dhnio as dhnio
    total_count = 0
    found = False
    while True:
        appList = dhnio.find_process([
            'dhnmain.exe',
            'dhnmain.py',
            'dhn.py',
            '/usr/bin/datahaven',
            'dhnview.exe',
            'dhnview.py',
            'dhnbackup.exe',
            'dhnbackup.py',
            'dhntester.exe',
            'dhntester.py',
            'dhnstarter.exe',
            ])
        if len(appList) > 0:
            found = True
        for pid in appList:
            dhnio.Dprint(0, 'trying to stop pid %d' % pid)
            dhnio.kill_process(pid)
        if len(appList) == 0:
            if found:
                dhnio.Dprint(0, 'DataHaven.NET stopped\n')
            else:
                dhnio.Dprint(0, 'DataHaven.NET was not started\n')
            return 0
        total_count += 1
        if total_count > 10:
            dhnio.Dprint(0, 'some DataHaven.NET process found, but can not stop it\n')
            return 1
        time.sleep(1)


def wait_than_kill(x):
    from twisted.internet import reactor
    import lib.dhnio as dhnio
    total_count = 0
    while True:
        appList = dhnio.find_process([
            'dhnmain.exe',
            'dhnmain.py',
            'dhn.py',
            '/usr/bin/datahaven',
            'dhnview.exe',
            'dhnview.py',
            'dhnbackup.exe',
            'dhnbackup.py',
            'dhntester.exe',
            'dhntester.py',
            'dhnstarter.exe',
            ])
        if len(appList) == 0:
            dhnio.Dprint(0, 'finished\n')
            reactor.stop()
            return 0
        total_count += 1
        if total_count > 10:
            dhnio.Dprint(0, 'not responding')
            ret = kill()
            reactor.stop()
            return ret
        time.sleep(1)


def main():
    try:
        import lib.dhnio as dhnio
    except:
        dirpath = os.path.dirname(os.path.abspath(sys.argv[0]))
        sys.path.insert(0, os.path.abspath('datahaven'))
        sys.path.insert(0, os.path.abspath(os.path.join(dirpath, '..')))
        sys.path.insert(0, os.path.abspath(os.path.join(dirpath, '..', '..')))
        try:
            import lib.dhnio as dhnio
        except:
            return 1

    # TODO
    # sys.excepthook = dhnio.ExceptionHook
    if not dhnio.isFrozen():
        from twisted.internet.defer import setDebugging
        setDebugging(True)

    # ask dhnio to count time for each line from that moment, not absolute time 
    dhnio.LifeBegins()

    # update locale
    dhnio.InstallLocale()
    
    # to be able to use "tail -f <log file>" command
    if dhnio.Linux():
        dhnio.UnbufferedSTDOUT()

    pars = parser()
    (opts, args) = pars.parse_args()

    if opts.no_logs:
        dhnio.DisableLogs()

    #---logpath---
    logpath = ''
    if dhnio.Windows():
        logpath = os.path.join(os.environ['APPDATA'], 'DataHaven.NET', 'logs', 'dhnmainstart.log')
    elif dhnio.Linux():
        old_path = os.path.join(os.path.expanduser('~'), 'datahavennet')
        if os.path.isdir(old_path):
            logpath = os.path.join(old_path, 'logs', 'dhnmainstart.log')
        else:
            logpath = os.path.join(os.path.expanduser('~'), '.datahaven', 'logs', 'dhnmainstart.log')

    if opts.output:
        logpath = opts.output

    if logpath != '':
        dhnio.OpenLogFile(logpath)
        dhnio.Dprint(2, 'dhnmain.main log file opened ' + logpath)
        if dhnio.Windows() and dhnio.isFrozen():
            dhnio.StdOutRedirectingStart()
            dhnio.Dprint(2, 'dhnmain.main redirecting started')

    if opts.debug or str(opts.debug) == '0':
        dhnio.SetDebug(opts.debug)

    if opts.quite and not opts.verbose:
        dhnio.DisableOutput()

    if opts.verbose:
        copyright()

    dhnio.Dprint(2, 'dhnmain.main started ' + time.asctime())

    overDict = override_options(opts, args)

    cmd = ''
    if len(args) > 0:
        cmd = args[0].lower()
        
    dhnio.Dprint(2, 'dhnmain.main args=%s' % str(args))

    #---start---
    if cmd == '' or cmd == 'start' or cmd == 'go':
        appList = dhnio.find_process([
            'dhnmain.exe',
            'dhnmain.py',
            'dhn.py',
            '/usr/bin/datahaven',
            ])
        if len(appList) > 0:
            dhnio.Dprint(0, 'found another process, pid=%s' % str(appList))
            dhnio.Dprint(0, 'DataHaven.NET already started.\n')
            return 0
        return run('', opts, args, overDict)

    #---show---
    elif cmd == 'show' or cmd == 'open':
        appList = dhnio.find_process([
            'dhnview.exe',
            'dhnview.py',
            ])
        if len(appList):
            dhnio.Dprint(0, 'found another dhnview process, pid=%s\n' % str(appList))
            return 0
        appList = dhnio.find_process([
            'dhnmain.exe',
            'dhnmain.py',
            'dhn.py',
            '/usr/bin/datahaven',
            ])
        if len(appList) == 0:
            return run('show', opts, args, overDict)
        
        dhnio.Dprint(0, 'found DataHaven.NET process, pid=%s\n' % str(appList))
        return show()

    #---stop---
    elif cmd == 'stop' or cmd == 'kill' or cmd == 'shutdown':
        appList = dhnio.find_process([
            'dhnmain.exe',
            'dhnmain.py',
            'dhn.py',
            '/usr/bin/datahaven',
            ])
        if len(appList) > 0:
            dhnio.Dprint(0, 'found main DataHaven.NET process...   ', '')
            try:
                from twisted.internet import reactor
                from command_line import run_url_command
                url = '?action=exit'
                run_url_command(url).addCallback(wait_than_kill)
                reactor.run()
                return 0
            except:
                dhnio.DprintException()
                return kill()
        else:
            dhnio.Dprint(0, 'DataHaven.NET is not running at the moment\n')
            return 0

    #---uninstall---
    elif cmd == 'uninstall':
        def do_spawn(x=None):
            from lib.settings import WindowsStarterFileName
            starter_filepath = os.path.join(dhnio.getExecutableDir(), WindowsStarterFileName())
            dhnio.Dprint(0, "dhnmain.main dhnstarter.exe path: %s " % starter_filepath)
            if not os.path.isfile(starter_filepath):
                dhnio.Dprint(0, "dhnmain.main ERROR %s not found" % starter_filepath)
                return 1
            cmdargs = [os.path.basename(starter_filepath), 'uninstall']
            dhnio.Dprint(0, "dhnmain.main os.spawnve cmdargs="+str(cmdargs))
            return os.spawnve(os.P_DETACH, starter_filepath, cmdargs, os.environ)
        def do_reactor_stop_and_spawn(x=None):
            reactor.stop()
            return do_spawn()
        dhnio.Dprint(0, 'dhnmain.main UNINSTALL!')
        if not dhnio.Windows():
            dhnio.Dprint(0, 'This command can be used only under OS Windows.')
            return 0
        if not dhnio.isFrozen():
            dhnio.Dprint(0, 'You are running DataHaven.NET from sources, uninstall command is available only for binary version.')
            return 0
        appList = dhnio.find_process(['dhnmain.exe',])
        if len(appList) > 0:
            dhnio.Dprint(0, 'found main DataHaven.NET process...   ', '')
            try:
                from twisted.internet import reactor
                from command_line import run_url_command
                url = '?action=exit'
                run_url_command(url).addCallback(do_reactor_stop_and_spawn)
                reactor.run()
                return 0
            except:
                dhnio.DprintException()
        return do_spawn()
        
    #---command_line---
    import command_line
    ret = command_line.run(opts, args, overDict, pars)
    if ret == 2:
        print usage()
    return ret 

#-------------------------------------------------------------------------------


def usage():
    try:
        import help
        return help.usage()
    except:
        return ''
    

def help():
    try:
        import help
        return help.help()
    except:
        return ''


def backup_schedule_format():
    try:
        import help
        return help.schedule_format()
    except:
        return ''


def copyright():
    print 'Copyright DataHaven.NET LTD. of Anguilla, 2006-2012. All rights reserved.'

#------------------------------------------------------------------------------ 


if __name__ == "__main__":
    ret = main()
    if ret == 2:
        print usage()
    sys.exit(ret)

