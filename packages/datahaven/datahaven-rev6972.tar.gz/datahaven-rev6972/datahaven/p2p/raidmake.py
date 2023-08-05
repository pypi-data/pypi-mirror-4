#!/usr/bin/python
#raidmake.py
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2012
#    Use of this software constitutes acceptance of the Terms of Use
#      http://datahaven.net/terms_of_use.html
#    All rights reserved.
#

#
# Input is a file and a RAID spec.
# The spec says for each datablock which parity blocks XOR it.
# As we read in each datablock we XOR all the parity blocks for it.
# Probably best to read in all the datablocks at once, and do all
# the parities one time.  If we did one datablock after another
# the parity blocks would need to be active all the time.
#
# If we XOR integers, we have a byte order issue probably, though
# maybe not since they all stay the same order, whatever that is.
#
# Some machines are 64-bit.  Would be fun to make use of that if
# we have it.
#
# 2^1 => 3       ^ is XOR operator
#
# Parity packets have to be a little longer so they can hold
# parities on signatures of datapackets.  So we can reconstruct
# those signatures.
#
#
import os
import sys
import struct
import time
import cStringIO


if __name__ == '__main__':
    dirpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    sys.path.insert(0, os.path.abspath(os.path.join(dirpath, '..', '..')))


import lib.eccmap as eccmap
import lib.misc as misc
import lib.dhnio as dhnio
import lib.settings as settings
import lib.tmpfile as tmpfile


#------------------------------------------------------------------------------ 

def raidmake(filename, eccmapname, backupId, blockNumber, data_parity_dir=None, in_memory=True):
    dhnio.Dprint(8, "raidmake.raidmake BEGIN %s %s %s %d" % (
        os.path.basename(filename), eccmapname, backupId, blockNumber))
    t = time.time()
    if in_memory:
        dataNum, parityNum, outDir = do_in_memory(filename, eccmapname, backupId, blockNumber, data_parity_dir)
    else:
        dataNum, parityNum, outDir = do_with_files(filename, eccmapname, backupId, blockNumber, data_parity_dir)
    dhnio.Dprint(8, "raidmake.raidmake END time=%.3f data=%d parity=%d" % (time.time()-t, dataNum, parityNum))
    return outDir


def do_in_memory(filename, eccmapname, backupId, blockNumber, data_parity_dir=None):
    if data_parity_dir is None:
        # data_parity_dir = tmpfile.subdir('data-par')
        data_parity_dir = settings.getLocalBackupsDir()

    myeccmap = eccmap.eccmap(eccmapname)
    INTSIZE = settings.IntSize()
    # any padding at end and block.Length fixes
    misc.RoundupFile(filename,myeccmap.datasegments*INTSIZE)     
    wholefile = dhnio.ReadBinaryFile(filename)
    length = len(wholefile)
    seglength = (length + myeccmap.datasegments - 1) / myeccmap.datasegments                 

    for DSegNum in range(myeccmap.datasegments):
        FileName = data_parity_dir + '/' + backupId + '-' + str(blockNumber) + '-' + str(DSegNum) + '-Data'
        #FileName = os.path.join(data_parity_dir, backupId + '-' + str(blockNumber) + '-' + str(DSegNum) + '-Data')
        f = open(FileName, "wb")
        segoffset = DSegNum * seglength
        for i in range(seglength):
            offset = segoffset + i;
            if offset < length:
                f.write(wholefile[offset])
            else:
                # any padding should go at the end of last seg 
                # and block.Length fixes
                f.write(" ")               
        f.close()
        
    dfds = {}
    for DSegNum in range(myeccmap.datasegments):
        FileName = data_parity_dir + '/' + backupId + '-' + str(blockNumber) + '-' + str(DSegNum) + '-Data'
        #FileName = os.path.join(data_parity_dir, backupId + '-' + str(blockNumber) + '-' + str(DSegNum) + '-Data')
        # instead of reading data from opened file 
        # we'l put it in memory 
        # and store current position in the data
        # so start from zero 
        #dfds[DSegNum] = [0, dhnio.ReadBinaryFile(FileName)]
        dfds[DSegNum] = cStringIO.StringIO(dhnio.ReadBinaryFile(FileName))

    pfds = {}
    for PSegNum in range(myeccmap.paritysegments):
        # we will keep parirty data in the momory
        # after doing all calculations
        # will write all parts on the disk
        pfds[PSegNum] = cStringIO.StringIO()

    #Parities = range(myeccmap.paritysegments)
    Parities = {}
    for i in range(seglength/INTSIZE):
        for PSegNum in range(myeccmap.paritysegments):
            Parities[PSegNum] = 0
        for DSegNum in range(myeccmap.datasegments):
            bstr = dfds[DSegNum].read(INTSIZE)
            #pos = dfds[DSegNum][0]
            #dfds[DSegNum][0] += INTSIZE
            #bstr = dfds[DSegNum][1][pos:pos+INTSIZE]
            if len(bstr) == INTSIZE:
                b, = struct.unpack(">l", bstr)
                Map = myeccmap.DataToParity[DSegNum]
                for PSegNum in Map:
                    if PSegNum > myeccmap.paritysegments:
                        dhnio.Dprint(2, "raidmake.raidmake PSegNum out of range " + str(PSegNum))
                        dhnio.Dprint(2, "raidmake.raidmake limit is " + str(myeccmap.paritysegments))
                        myeccmap.check()
                        raise Exception("eccmap error")
                    Parities[PSegNum] = Parities[PSegNum] ^ b
            else:
                raise Exception('strange read under INTSIZE bytes, len(bstr)=%d DSegNum=%d' % (len(bstr), DSegNum)) 
                #TODO
                #dhnio.Dprint(2, 'raidmake.raidmake WARNING strange read under INTSIZE bytes')
                #dhnio.Dprint(2, 'raidmake.raidmake len(bstr)=%s DSegNum=%s' % (str(len(bstr)), str(DSegNum)))

        for PSegNum in range(myeccmap.paritysegments):
            bstr = struct.pack(">l", Parities[PSegNum])
            #pfds[PSegNum] += bstr
            pfds[PSegNum].write(bstr)

    dataNum = len(dfds)
    parityNum = len(pfds)
    
    for PSegNum, data in pfds.items():
        #FileName = os.path.join(data_parity_dir, backupId + '-' + str(blockNumber) + '-' + str(PSegNum) + '-Parity')
        FileName = data_parity_dir + '/' + backupId + '-' + str(blockNumber) + '-' + str(PSegNum) + '-Parity'
        dhnio.WriteFile(FileName, pfds[PSegNum].getvalue())

    for f in dfds.values():
        f.close()
        #dataNum += 1

    for f in pfds.values():
        f.close()
        #parityNum += 1
    
    del dfds
    del pfds
    del Parities

    return dataNum, parityNum, data_parity_dir


def do_with_files(filename, eccmapname, backupId, blockNumber, data_parity_dir=None):
    if data_parity_dir is None:
        # data_parity_dir = tmpfile.subdir('data-par')
        data_parity_dir = settings.getLocalBackupsDir()

    myeccmap = eccmap.eccmap(eccmapname)
    INTSIZE = settings.IntSize()
    misc.RoundupFile(filename,myeccmap.datasegments*INTSIZE)      # any padding at end and block.Length fixes
    wholefile = dhnio.ReadBinaryFile(filename)
    length = len(wholefile)
    seglength = (length + myeccmap.datasegments - 1)/myeccmap.datasegments                 # PREPRO -

    for DSegNum in range(myeccmap.datasegments):
        FileName = data_parity_dir + '/' + backupId + '-' + str(blockNumber) + '-' + str(DSegNum) + '-Data'
        f = open(FileName, "wb")
        segoffset = DSegNum * seglength
        for i in range(seglength):
            offset = segoffset + i;
            if (offset < length):
                f.write(wholefile[offset])
            else:
                # any padding should go at the end of last seg 
                # and block.Length fixes
                f.write(" ")               
        f.close()
    del wholefile

    #dfds = range(myeccmap.datasegments)
    dfds = {}
    for DSegNum in range(myeccmap.datasegments):
        FileName = data_parity_dir + '/' + backupId + '-' + str(blockNumber) + '-' + str(DSegNum) + '-Data'
        dfds[DSegNum] = open(FileName, "rb")

    #pfds = range(myeccmap.paritysegments)
    pfds = {}
    for PSegNum in range(myeccmap.paritysegments):
        FileName = data_parity_dir + '/' + backupId + '-' + str(blockNumber) + '-' + str(PSegNum) + '-Parity'
        pfds[PSegNum] = open(FileName, "wb")

    #Parities = range(myeccmap.paritysegments)
    Parities = {}
    for i in range(seglength/INTSIZE):
        for PSegNum in range(myeccmap.paritysegments):
            Parities[PSegNum] = 0
        for DSegNum in range(myeccmap.datasegments):
            bstr = dfds[DSegNum].read(INTSIZE)
            if len(bstr) == INTSIZE:
                b, = struct.unpack(">l", bstr)
                Map = myeccmap.DataToParity[DSegNum]
                for PSegNum in Map:
                    if PSegNum > myeccmap.paritysegments:
                        dhnio.Dprint(2, "raidmake.raidmake PSegNum out of range " + str(PSegNum))
                        dhnio.Dprint(2, "raidmake.raidmake limit is " + str(myeccmap.paritysegments))
                        myeccmap.check()
                        raise Exception("eccmap error")
                    Parities[PSegNum] = Parities[PSegNum] ^ b
            else :
                #TODO
                dhnio.Dprint(2, 'raidmake.raidmake WARNING strange read under INTSIZE bytes')
                dhnio.Dprint(2, 'raidmake.raidmake len(bstr)=%s DSegNum=%s' % (str(len(bstr)), str(DSegNum)))

        for PSegNum in range(myeccmap.paritysegments):
            bstr = struct.pack(">l", Parities[PSegNum])
            pfds[PSegNum].write(bstr)

    dataNum = 0
    parityNum = 0
    
    for f in dfds.values():
        f.close()
        dataNum += 1

    for f in pfds.values():
        f.close()
        parityNum += 1

    del dfds
    del pfds
    del Parities

    return dataNum, parityNum, data_parity_dir



def main():
    dhnio.SetDebug(18)
    raidmake(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5], sys.argv[6]=='1')
    

if __name__ == "__main__":
    main()



