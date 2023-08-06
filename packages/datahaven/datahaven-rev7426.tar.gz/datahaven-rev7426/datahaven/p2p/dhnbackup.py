#!/usr/bin/python
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2012
#    Use of this software constitutes acceptance of the Terms of Use
#      http://datahaven.net/terms_of_use.html
#    All rights reserved.
#
#  http://docs.python.org/lib/tar-examples.html
#
#  This python code can be used to replace the Unix tar command
#  and so be portable to non-unix machines.
#
#  There are other python tar libraries, but this is included with python.
#
#  If we kept track of how far we were through a list of files, and broke off
#    new dhnblocks at file boundaries, we could restart a backup and continue
#    were we left off if a crash happened while we were waiting to send a block
#    (most of the time is waiting so good chance).
#
#  *************  WARNING ***************
#  Note that we should not print things here because tar output goes to standard out.
#  If we print anything else to stdout the .tar file will be ruined.
#  We must also not print things in anything this calls.
#  *************  WARNING ***************

import os
import sys
import platform
import tarfile


try:
    import msvcrt
    msvcrt.setmode(1, os.O_BINARY)
except:
    pass


def printlog(txt):
    LogFile = open('dhnbackup.log', 'a')
    LogFile.write(txt)
    LogFile.close()



def _LinuxExcludeFunction(filename): 
    # filename comes in with the path relative to the start path, 
    # so dirbeingbackedup/photos/christmas2008.jpg
    if filename.find("datahavennet") != -1 :
        return True
    if filename.find(".datahaven") != -1 :
        return True
    # PREPRO  
    #   On linux we should test for the attribute meaning "nodump" or "nobackup"
    # This is set with
    #     chattr +d  file
    #   And listed with 
    #     lsattr file
    #  Also should test that the file is readable and maybe that directory is executable. 
    #  If tar gets stuff it can not read it just stops.
    return False # don't exclude the file

def _WindowsExcludeFunction(filename): 
    # filename comes in with the path relative to the start path, 
    # so "Local Settings\Application Data\Microsoft\Windows\UsrClass.dat"
    # on windows I run into some files that Windows tells me 
    # I don't have permission to open (system files), 
    # I had hoped to use "os.access(filename, os.R_OK) == False" 
    # to skip a file if I couldn't read it, 
    # but I did not get it to work every time. DWC
    if (filename.lower().find("local settings\\temp") != -1) or (filename.lower().find("datahaven.net") != -1) :
        return True
    return False # don't exclude the file


_ExcludeFunction = _LinuxExcludeFunction
if platform.uname()[0] == 'Windows':
    _ExcludeFunction = _WindowsExcludeFunction

    
def writetar(filelist, subdirs=True):
    tar = tarfile.open('', "w|", fileobj=sys.stdout )

    # if we have python 2.6 then we can use an exclude function
    if sys.hexversion >= 0x2060100:
        for name in filelist:
            tar.add(name, None, subdirs, _ExcludeFunction) # the True is for recursive, if we wanted to just do the immediate directory set to False
            if not subdirs:
                for file in os.listdir(name):
                    if not os.path.isdir(os.path.join(name,file)): 
                        tar.add(os.path.join(name,file), None, subdirs, _ExcludeFunction) # the True is for recursive, if we wanted to just do the immediate directory set to False

    else: # otherwise no exclude function
        for name in filelist:
            tar.add(name, None, subdirs)
            if not subdirs:
                for file in os.listdir(name):
                    if not os.path.isdir(os.path.join(name,file)): 
                        tar.add(os.path.join(name,file), None, subdirs) 

    tar.close()

#def readtar():
#    tar = tarfile.open(mode="r|", fileobj=sys.stdin)
#    for tarinfo in tar:
#        tar.extract(tarinfo)
#    tar.close()

def main():
    if len(sys.argv) < 3:
        printlog('sys.argv: %s\n' % str(sys.argv))
        printlog('dhnbackup ["subdirs"/"nosubdirs"] [folder path]\n')
        sys.exit(2)

#    subdirs = True
#    if sys.argv[1].strip().lower() == 'nosubdirs':
#        subdirs = False

#    archiveDir = sys.argv[2]
#    for i in range(2, len(sys.argv)):
#        archiveDir = archiveDir + sys.argv[i] + ' '

    writetar([sys.argv[2]], sys.argv[1].strip().lower() != 'nosubdirs')


if __name__ == "__main__":
    main()


