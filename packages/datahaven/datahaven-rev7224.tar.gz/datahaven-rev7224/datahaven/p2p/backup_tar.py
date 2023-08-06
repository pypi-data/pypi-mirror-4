#!/usr/bin/python
#backup_tar.py
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2012
#    Use of this software constitutes acceptance of the Terms of Use
#      http://datahaven.net/terms_of_use.html
#    All rights reserved.
#
#  We want a pipe output or input so we don't need to store intermediate data.
#
#  The popen starts another process.  That process can block but we don't.
#  backup.py only takes data from this pipe when it is ready.

import os
import sys
import subprocess


import lib.nonblocking as nonblocking
import lib.dhnio as dhnio


# Returns file descriptor for process that makes tar archive
def backuptar(directorypath, recursive_subfolders=True):
    if not os.path.isdir(directorypath):
        dhnio.Dprint(1, 'backup_tar.backuptar ERROR %s not found' % directorypath)
        return None

    subdirs = 'subdirs'
    if not recursive_subfolders:
        subdirs = 'nosubdirs'

    dhnio.Dprint(6, "backup_tar.backuptar %s %s" % (directorypath, subdirs))

    if dhnio.Windows():
        if dhnio.isFrozen():
            commandpath = "dhnbackup.exe"
            cmdargs = [commandpath, subdirs, directorypath]
        else:
            commandpath = "dhnbackup.py"
            cmdargs = ['python.exe', commandpath, subdirs, directorypath]
    else:
        commandpath = "dhnbackup.py"
        cmdargs = ['python', commandpath, subdirs, directorypath]

    if not os.path.isfile(commandpath):
        dhnio.Dprint(1, 'backup_tar.backuptar ERROR %s not found' % commandpath)
        return None

    dhnio.Dprint(6, "backup_tar.backuptar going to execute %s" % str(cmdargs))

    try:
        if dhnio.Windows():
            import win32process
            p = nonblocking.Popen(
                cmdargs,
                shell=False,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=False,
                creationflags = win32process.CREATE_NO_WINDOW,)
        else:
            p = nonblocking.Popen(
                cmdargs,
                shell=False,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=False,)
    except:
        dhnio.Dprint(1, 'backup_tar.backuptar ERROR executing: ' + str(cmdargs) + str(dhnio.formatExceptionInfo()))
        return None

    return p




