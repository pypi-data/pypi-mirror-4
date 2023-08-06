#!/usr/bin/python
#dhn.py
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2012
#    Use of this software constitutes acceptance of the Terms of Use
#      http://datahaven.net/terms_of_use.html
#    All rights reserved.
#

import os
import sys


def windows_and_frozen():
    import platform
    if platform.uname()[0] != 'Windows':
        # return False
        # under Linux we have same problem too ...
        # I have no idea!
        return True

    #http://www.py2exe.org/index.cgi/HowToDetermineIfRunningFromExe
    import imp
    return  (hasattr(sys, "frozen") or # new py2exe
            hasattr(sys, "importers") or# old py2exe
            imp.is_frozen("__main__")) # tools/freeze



if __name__ == "__main__":

    how_to_stop = windows_and_frozen()

    import p2p.dhnmain
    ret = p2p.dhnmain.main()

    # we use py2exe to build DataHaven.NET under Windows
    # but it wont finish correctly!
    # after finishing all process dhnmain.exe still working
    # and eat 50% CPU! - it wont stop.
    # but if you running from command line - it gives no problems
    # ... it seems CSpace reactor make some conflicts with twisted reactor
    # however all threads are finished correctly - really strange thing ...
    # TODO I definately should find where is the problem here.
    # but let's take this for now ... it is working.
    
    if how_to_stop:
        os._exit(ret)
    else:
        sys.exit(ret)

