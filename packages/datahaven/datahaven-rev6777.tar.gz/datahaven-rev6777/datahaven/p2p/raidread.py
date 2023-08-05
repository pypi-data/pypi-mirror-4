#!/usr/bin/python
#raidread.py
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2012
#    All rights reserved.
#

#
# This is to read some possibly incomplete raid data and recover original data.
#
# Basic idea is to find a parity that is only missing one data, then fix that
#  data, and look at parities again to see if another is now missing only one.
#  This can be called an "iterative algorithm" or "belief propagation".
#  There are algorithms that can recover data when this can not, but
#    they are more complicated.
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
# 2^1 => 3       ^ is XOR operator  - so maybe we can do it in Python
#
# In the production code, when there are multiple errors we really want
# to fix the one we can fix fastest first.  The only danger is that
# we get too many errors at the same time.  We reduce this danger if
# we fix the one we can fix fastest first.


import struct
import os
import sys


import lib.eccmap as eccmap
import lib.misc as misc
import lib.dhnio as dhnio
import lib.settings as settings
import lib.tmpfile as tmpfile

#------------------------------------------------------------------------------ 

def unpack_nbyte(number):
    result = long(0)
    for i in range(0,len(number)):
        result = 256*result + ord(number[i])
    return result

def RebuildOne(inlist, listlen, outfilename):
    RebuildOne_new(inlist, listlen, outfilename)

#rebuildOne_new, new2, and orig are just for debugging purposes
def RebuildOne_new(inlist, listlen, outfilename):
##    print "inlist=" + str(inlist)
##    print "inlist=" + str(listlen)
##    print "We can rebuild one " + outfilename + "\n"

    readsize = 1 # vary from 1 byte to 4 bytes

    raidfiles = range(listlen)   # just need a list of this size
    raidreads = range(listlen)
    for filenum in range(listlen):
        raidfiles[filenum] = open(inlist[filenum], "rb")
    rebuildfile = open(outfilename,"wb")

    loopcount = 0
    debugLoopcount = 2000
    debugI = 2000
    while 1:
#        if loopcount > debugLoopcount:
#            print "loopcount=" + str(loopcount)
        for k in range(listlen):
            raidreads[k] = raidfiles[k].read(2048)
#            if loopcount > debugLoopcount:
#                print "file" + str(i) + ", " + inlist[i] + " len=" + str(len(raidreads[i]))
        if not raidreads[0]:
            break
        i = 0
        while i < len(raidreads[0]):
            xor = 0
#            if loopcount > debugLoopcount and i > debugI:
#                print "i=" + str(i) + ", len=" + str(len(raidreads[0]))
#                print "listlen=" + str(listlen)
            for j in range(listlen):
#                if loopcount > debugLoopcount and i > debugI:
#                    print str(len(raidreads[j]))
                b1 = ord(raidreads[j][i])
                xor = xor ^ b1
#                if loopcount > debugLoopcount and i > debugI:
#                    print "j=" + str(j) + ", val=" + str(b1)
#            if loopcount > debugLoopcount and i>debugI:
#                print "loopcount=" + str(loopcount) + ", i=" + str(i) + ", len=" + str(len(raidreads[0]))

            rebuildfile.write(chr(xor))
            i += readsize
#        loopcount += 1

    for filenum in range(listlen):
        raidfiles[filenum].close()
        
    rebuildfile.close()


def RebuildOne_new2(inlist, listlen, outfilename):
    INTSIZE=settings.IntSize()
    fds = range(0,listlen)   # just need a list of this size
##    print "inlist=" + str(inlist)
##    print "inlist=" + str(listlen)
##    print "We can rebuild one " + outfilename + "\n"
    wholefile = dhnio.ReadBinaryFile(inlist[0])
    seglength = len(wholefile)   # just needed length of file
    for filenum in range(0, listlen):
        fds[filenum]=open(inlist[filenum],"r")
    fout = open(outfilename,"w")
    for i in range(0,seglength):
        xor = 0
        for j in range(0,listlen):
##            print "reading byte " + str(i) + " in file " + inlist[j]
            b1 = ord(fds[j].read(1))
##            print " val=" + str(b1)
            xor = xor ^ b1
        fout.write(chr(xor))
    for filenum in range(0, listlen):
        fds[filenum].close

# We XOR list of listlen input files and write result to a file named outfilename
def RebuildOne_orig(inlist, listlen, outfilename):
        INTSIZE=settings.IntSize()
        fds = range(0,listlen)   # just need a list of this size
##        print "We can rebuild one " + outfilename + "\n"
        wholefile = dhnio.ReadBinaryFile(inlist[0])
        seglength=len(wholefile)   # just needed length of file
        for filenum in range(0, listlen):
                fds[filenum]=open(inlist[filenum],"rb")
        fout=open(outfilename,"w")
        for i in range(0,seglength/INTSIZE):
                xor=0
                for j in range(0, listlen):
                        bstr1 = fds[j].read(INTSIZE)
                        #b1 = unpack_nbyte(bstr1)
                        b1, = struct.unpack(">l", bstr1)
                        xor = xor ^ b1
                outstr = struct.pack(">l", xor)
                fout.write(outstr)
        for filenum in range(0, listlen):
                fds[filenum].close


# If segment is good, there is a file for it, if not then no file exists.
# We only rebuild data segments.
# Could only make parity segments from existing data segments, so no help toward getting data.
# As long as we could rebuild one more data segment in a pass,
#  we do another pass to see if we are then able to do another.
#  When we can't do anything more we could how many good data segments there
#    are, and if we have all we win, if not we fail.

def raidread(OutputFileName, eccmapname, backupId, blockNumber, data_parity_dir=None):
    if data_parity_dir is None:
        # data_parity_dir = tmpfile.subdir('data-par')
        data_parity_dir = settings.getLocalBackupsDir()

    INTSIZE = settings.IntSize()
    myeccmap = eccmap.eccmap(eccmapname)
    GoodFiles = range(0, 200)

    MakingProgress = 1
    while MakingProgress == 1:
        MakingProgress = 0
        for PSegNum in range(myeccmap.paritysegments):
                PFileName = os.path.join(data_parity_dir, backupId + '-' + str(blockNumber) + '-' + str(PSegNum) + '-Parity')
                
                if os.path.exists(PFileName):
                        Map = myeccmap.ParityToData[PSegNum]
                        TotalDSegs = 0
                        GoodDSegs = 0
                        for DSegNum in Map:
                                TotalDSegs+=1
                                FileName = os.path.join(data_parity_dir, backupId + '-' + str(blockNumber) + '-' + str(DSegNum) + '-Data')
                                if os.path.exists(FileName):
                                        GoodFiles[GoodDSegs]=FileName
                                        GoodDSegs+=1
                                else:
                                        BadName=FileName
                        if GoodDSegs == TotalDSegs - 1:
##                                print "We can rebuild one " + BadName + "\n"
                                MakingProgress=1
                                GoodFiles[GoodDSegs]=PFileName
                                GoodDSegs+=1
                                RebuildOne(GoodFiles,GoodDSegs,BadName)

    #  Count up the good segments and combine
    GoodDSegs = 0
    output = open(OutputFileName,"wb")
    for DSegNum in range(myeccmap.datasegments):
        FileName = os.path.join(data_parity_dir, backupId + '-' + str(blockNumber) + '-' + str(DSegNum) + '-Data')
        if os.path.exists(FileName):
                GoodDSegs+=1
                moredata=open(FileName,"rb").read()
                output.write(moredata)
    output.close()
##    if(GoodDSegs == myeccmap.datasegments):
##        print "We got them all"
##    else:
##        print "We could not make all data segments"


def main():
    if (len(sys.argv) < 3):
        print "raidread needs an output filename and eccmap name"
        sys.exit(2)

    OutputFileName = sys.argv[1]
    eccmapname = sys.argv[2]

    print "raidread is starting with"
    print OutputFileName
    print eccmapname
    raidread(OutputFileName, eccmapname)


if __name__ == "__main__":
    main()


