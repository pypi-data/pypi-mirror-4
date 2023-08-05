#!/usr/bin/python
#tmpfile.py
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2012
#    All rights reserved.
#


import os
import tempfile
import time


from twisted.internet import reactor, task


import dhnio


_TempDirPath = None
_FilesDict = {}
_CollectorTask = None
_SubDirs = {

    'outbox':   60*60*24*1,
    # hold onto outbox files 1 day
    # so we can handle resends if contact offline

    # 'data-par': 0,
    # for data and parity files we have special rules
    # because both files types are stored in the same folder "data-par"
    # also backup_monitor seems to be responsible to remove these files
    # but we will remove old files too at startup
    # hold onto data for rebuilding for a day, can rebuild parity as needed
    # hold onto parity for an hour

    'tcp-in':   60*10,
    # 10 minutes for incoming tcp files

    'ssh-in':   60*10,
    # 10 minutes for incoming ssh files

    'q2q-in':   60*10,
    # 10 minutes for incoming files

    'http-in':  60*30,
    # 30 minutes for incoming http files
    # http is very slow so let's give more time

    'email-in': 60*60,
    # 1 hour for incoming email files
    # email is so slow so we may be want to keep it more

    'cspace-in':60*10,
    # 10 minutes for incoming files
    
    'bat':      60*60,
    # we need bat files to restart dhn
    # we create it and start immediately
    # so we can remove it soon

    'propagat': 60*10,
    # propagate happens often enough,
    # 10 minutes should be enough

    'backup':   60*10,
    # 10 minutes for backup files

    'other':    0,
    # other files. do not know when to remove
    # they can be even in another location
    # use register(name, filename)

    }



#------------------------------------------------------------------------------


def init(temp_dir_path=''):
    dhnio.Dprint(4, 'tmpfile.init')
    global _TempDirPath
    global _SubDirs
    global _FilesDict
    global _CollectorTask

    if _TempDirPath is None:
        if temp_dir_path != '':
            _TempDirPath = temp_dir_path
        else:
            os_temp_dir = tempfile.gettempdir()
            temp_dir = os.path.join(os_temp_dir, 'dhn')

            if not os.path.exists(temp_dir):
                try:
                    os.mkdir(temp_dir)
                except:
                    dhnio.Dprint(2, 'tmpfile.init ERROR can not create ' + temp_dir)
                    dhnio.DprintException()
                    temp_dir = os_temp_dir

            if not os.access(temp_dir, os.W_OK):
                dhnio.Dprint(2, 'tmpfile.init ERROR no write permissions to ' + temp_dir)
                temp_dir = os_temp_dir

            _TempDirPath = temp_dir
        dhnio.Dprint(6, 'tmpfile.init  _TempDirPath=' + _TempDirPath)

    for name in _SubDirs.keys():
        if not os.path.exists(subdir(name)):
            try:
                os.makedirs(subdir(name))
            except:
                dhnio.Dprint(2, 'tmpfile.init ERROR can not create ' + subdir(name))
                dhnio.DprintException()

    for name in _SubDirs.keys():
        if not _FilesDict.has_key(name):
            _FilesDict[name] = {}

    startup_clean()

    if _CollectorTask is None:
        _CollectorTask = task.LoopingCall(collect)
        _CollectorTask.start(60)


def shutdown():
    # we do not want to remove any files here
    # just stop the collector task
    dhnio.Dprint(4, 'tmpfile.shutdown')
    global _CollectorTask
    if _CollectorTask is not None:
        _CollectorTask.stop()
        del _CollectorTask
        _CollectorTask = None


def subdir(name):
    global _TempDirPath
    if _TempDirPath is None:
        init()
    return os.path.join(_TempDirPath, name)


def register(filepath):
    global _FilesDict
    subdir, filename = os.path.split(filepath)
    name = os.path.basename(subdir)
    if name not in _FilesDict.keys():
        name = 'other'
    _FilesDict[name][filepath] = time.time()


# make a new file under sub folder name
# return it's file descriptor and path
# remember you need to close the file descriptor. by your self
# tmpfile will remove it later - do not worry.
def make(name, extension='', prefix=''):
    global _TempDirPath
    global _FilesDict
    if _TempDirPath is None:
        init()

    if name not in _FilesDict.keys():
        name = 'other'
    try:
        fd, filename = tempfile.mkstemp(extension, prefix, subdir(name))
        _FilesDict[name][filename] = time.time()
    except:
        dhnio.Dprint(1, 'tmpfile.make ERROR creating file in sub folder ' + name)
        dhnio.DprintException()
        return None, ''
    dhnio.Dprint(12, 'tmpfile.make ' + filename)
    return fd, filename


def erase(name, filename):
    global _FilesDict
    if name in _FilesDict.keys():
        try:
            _FilesDict[name].pop(filename, '')
        except:
            dhnio.Dprint(4, 'tmpfile.erase WARNING we do not know about file %s in sub folder %s' %(filename, name))
    else:
        dhnio.Dprint(4, 'tmpfile.erase WARNING we do not know sub folder ' + name)

    if not os.path.exists(filename):
        dhnio.Dprint(12, 'tmpfile.erase WARNING %s not exist' % filename)
        return

    if not os.access(filename, os.W_OK):
        dhnio.Dprint(4, 'tmpfile.erase WARNING %s no write permissions' % filename)
        return

    try:
        os.remove(filename)
        dhnio.Dprint(12, 'tmpfile.erase ' + filename)
    except:
        dhnio.Dprint(2, 'tmpfile.erase ERROR can not remove ' + filename)
        #dhnio.DprintException()


def throw_out(filepath):
    global _FilesDict
    global _SubDirs
    subdir, filename = os.path.split(filepath)
    name = os.path.basename(subdir)
    erase(name, filepath)
    #delay = 1
    #if name == 'outbox':
        #delay = 60*60
    #reactor.callLater(delay, erase, name, filepath)


def collect():
    # remove old files
    dhnio.Dprint(10, 'tmpfile.collect')
    global _FilesDict
    global _SubDirs
    erase_list = []
    for name in _FilesDict.keys():
        # for data and parity files we have special rules
        # we do not want to remove Data or Parity here.
        # backup_monitor should take care of this.
        if name == 'data-par':
            continue
#            for filename, filetime in _FilesDict[name].items():
#                if filename.lower().enswith('-data'):
#                    # hold onto data for rebuilding for a day,
#                    # can rebuild parity as needed
#                    if time.time() - filetime > 60*60*24*1:
#                        erase_list.append((name, filename))
#                elif filename.lower().endswith('-parity'):
#                    # hold onto parity for an hour
#                    if time.time() - filetime > 60*60:
#                        erase_list.append((name, filename))

        else:
            # how long we want to keep the file?
            lifetime = _SubDirs.get(name, 0)
            # if this is not set - keep forever
            if lifetime == 0:
                continue
            for filename, filetime in _FilesDict[name].items():
                # if file is too old - remove it
                if time.time() - filetime > lifetime:
                    erase_list.append((name, filename))

    for name, filename in erase_list:
        erase(name, filename)

    del erase_list


def startup_clean():
    # at startup we want to scan all sub folders
    # and remove the old files
    # we will get creation time with os.stat
    dhnio.Dprint(6, 'tmpfile.startup_clean')
    global _TempDirPath
    if _TempDirPath is None:
        return
    global _SubDirs
    for name in os.listdir(_TempDirPath):
        # we want to scan only our folders
        # do not want to be responsible of other files
        if name not in _SubDirs.keys():
            continue

        # for data and parity files we have special rules
        # we do not want to remove Data or Parity here.
        # backup_monitor should take care of this.
        if name == 'data-par':
            pass
#            for filename in os.listdir(subdir(name)):
#                filepath = os.path.join(subdir(name), filename)
#                filetime = os.stat(filepath).st_ctime
#                if filename.lower().endswith('-data'):
#                    # hold onto data for rebuilding for a day,
#                    # can rebuild parity as needed
#                    if time.time() - filetime > 60*60*24*1:
#                        erase(name, filepath)
#                elif filename.lower().endswith('-parity'):
#                    # hold onto parity for an hour
#                    if time.time() - filetime > 60*60:
#                        erase(name, filepath)

        else:
            lifetime = _SubDirs.get(name, 0)
            if lifetime == 0:
                continue
            for filename in os.listdir(subdir(name)):
                filepath = os.path.join(subdir(name), filename)
                filetime = os.stat(filepath).st_ctime
                if time.time() - filetime > lifetime:
                    erase(name, filepath)



#------------------------------------------------------------------------------


if __name__ == '__main__':
    dhnio.SetDebug(18)
    init()
    fd, filename = make('bat', '.bat')
    os.write(fd, 'TEST FILE')
    os.close(fd)
    from twisted.internet import reactor
    reactor.run()




