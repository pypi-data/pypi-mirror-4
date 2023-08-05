#!/usr/bin/python
#localtester.py
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2012
#    Use of this software constitutes acceptance of the Terms of Use
#      http://datahaven.net/terms_of_use.html
#    All rights reserved.
#
#
# Checks that customer dhnpackets on the local disk still have good signatures.
# These packets could be outgoing, cached, incoming, or stored for remote customers.
# Idea is to detect bit-rot and then either if there is a problem we can do different
# things depending on what type it is.  So far:
#   1) If data we store for a remote customer :  ask for the packet again (he may call his scrubber)
#   2) If just cache of our personal data stored somewhere:  just delete bad packet from cache
#
# Also, after a system crash we need to check that things are ok and cleanup
# and partial stuff, like maybe backupid/outgoing/tmp where block was being
# converted to a bunch of packets but the conversion was not finished.
#
# So has to open/parse the dhnpacket but that code is part of dhnpacket.py
#
# The concept of "fail fast" is what we are after here.  If there is a failure we
# want to know about it fast, so we can fix it fast, so the chance of multiple
# failures at the same time is less.

import os
import sys
import time
import string


try:
    from twisted.internet import reactor
except:
    sys.exit('Error initializing twisted.internet.reactor in localtester.py')

from twisted.python.win32 import cmdLineQuote

import subprocess


if __name__ == "__main__":
    sys.path.append(os.path.join('..','..'))
    sys.path.append('datahaven')

import lib.dhnio as dhnio
import lib.settings as settings
import lib.nonblocking as nonblocking


#-------------------------------------------------------------------------------

TesterUpdateCustomers = 'update_customers'
TesterValidate = 'validate'
TesterSpaceTime = 'space_time'

_TesterQueue = []
_CurrentProcess = None
_Loop = None
_LoopValidate = None
_LoopUpdateCustomers = None


def _pushTester(Tester):
    global _TesterQueue
    if Tester in _TesterQueue:
        return
    _TesterQueue.append(Tester)

def _popTester():
    global _TesterQueue
    if len(_TesterQueue) == 0:
        return None
    Tester = _TesterQueue[0]
    del _TesterQueue[0]
    return Tester

#-------------------------------------------------------------------------------

def run(Tester):
    global _CurrentProcess
    dhnio.Dprint(8, 'localtester.run ' + str(Tester))

    if dhnio.isFrozen() and dhnio.Windows():
        commandpath = 'dhntester.exe'
        cmdargs = [commandpath, Tester]
    else:
        commandpath = 'dhntester.py'
        cmdargs = ['python', commandpath, Tester]

    if not os.path.isfile(commandpath):
        dhnio.Dprint(1, 'localtester.run ERROR %s not found' % commandpath)
        return None

    dhnio.Dprint(6, 'localtester.run execute: %s' % cmdargs)

    try:
        if dhnio.Windows():
            import win32process
            _CurrentProcess = nonblocking.Popen(
                cmdargs,
                shell = True,
                stdin = subprocess.PIPE,
                stdout = subprocess.PIPE,
                stderr = subprocess.PIPE,
                universal_newlines = False,
                creationflags = win32process.CREATE_NO_WINDOW,)
        else:
            _CurrentProcess = nonblocking.Popen(
                cmdargs,
                shell = True,
                stdin = subprocess.PIPE,
                stdout = subprocess.PIPE,
                stderr = subprocess.PIPE,
                universal_newlines = False,)
    except:
        dhnio.Dprint(1, 'localtester.run ERROR executing: %s' % str(cmd))
        dhnio.DprintException()


def alive():
    global _CurrentProcess
    if _CurrentProcess is None:
        return False
    try:
        p = _CurrentProcess.poll()
    except:
        return False
    return p is None

def loop():
    global _Loop
    dhnio.Dprint(15, 'localtester.loop')
    if not alive():
        Tester = _popTester()
        if Tester:
            run(Tester)
    _Loop = reactor.callLater(settings.DefaultLocaltesterLoop(), loop)

def loop_validate():
    global _LoopValidate
##    dhnio.Dprint(6, 'localtester.loop_validate')
    TestValid()
    _LoopValidate = reactor.callLater(settings.DefaultLocaltesterValidateTimeout(), loop_validate)

def loop_update_customers():
    global _LoopUpdateCustomers
    TestUpdateCustomers()
    _LoopUpdateCustomers = reactor.callLater(settings.DefaultLocaltesterUpdateCustomersTimeout(), loop_update_customers)

#-------------------------------------------------------------------------------

def TestUpdateCustomers():
    dhnio.Dprint(10, 'localtester.TestUpdateCustomers')
    _pushTester(TesterUpdateCustomers)

def TestValid():
    dhnio.Dprint(10, 'localtester.TestValid')
    _pushTester(TesterValidate)

def TestSpaceTime():
    dhnio.Dprint(10, 'localtester.TestSpaceTime')
    _pushTester(TesterSpaceTime)

def init():
    global _Loop
    global _LoopValidate
    global _LoopUpdateCustomers
    dhnio.Dprint(4, 'localtester.init ')
    _Loop = reactor.callLater(0, loop)
    _LoopValidate = reactor.callLater(5, loop_validate)
    _LoopUpdateCustomers = reactor.callLater(10, loop_update_customers)

def shutdown():
    global _Loop
    global _LoopValidate
    global _LoopUpdateCustomers
    global _CurrentProcess
    dhnio.Dprint(4, 'localtester.shutdown ')

    if _Loop:
        if not _Loop.cancelled:
            _Loop.cancel()
    if _LoopValidate:
        if not _LoopValidate.cancelled:
            _LoopValidate.cancel()
    if _LoopUpdateCustomers:
        if not _LoopUpdateCustomers.cancelled:
            _LoopUpdateCustomers.cancel()

    if alive():
        dhnio.Dprint(4, 'localtester.shutdown is killing dhntester')

        try:
            _CurrentProcess.kill()
        except:
            dhnio.Dprint(4, 'localtester.shutdown WARNING can not kill dhntester')
        del _CurrentProcess
        _CurrentProcess = None




#-------------------------------------------------------------------------------

if __name__ == "__main__":
    dhnio.SetDebug(18)
    settings.init()
    init()
    reactor.run()

##class localcustdatatest(unittest.TestCase):
##    def test_custdata(self):
##        localtester()

