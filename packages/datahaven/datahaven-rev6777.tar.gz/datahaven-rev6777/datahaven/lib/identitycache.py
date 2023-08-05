#!/usr/bin/python
#identitycache.py
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2012
#    All rights reserved.
#
#
# This fetches identities off the web and stores an xml copy in file and an identity object
#  in a dictionary.  Other parts of DHN call this to get an identity using an IDURL.

import os


from twisted.internet.defer import Deferred


import dhnio
import dhnnet
import settings
import identitydb


_CachingTasks = {}


#-------------------------------------------------------------------------------


def init(success_func=None, fail_func=None):
    dhnio.Dprint(4, 'identitycache.init')
    identitydb.init()
    CacheCentralID(success_func, fail_func)

def CacheCentralID(success_func=None, fail_func=None):
    dhnio.Dprint(6, 'identitycache.CacheCentralID')
    if HasKey(settings.CentralID()):
        if success_func:
            success_func('')
        return
    #src = dhnio._read_data(os.path.join(dhnio.getExecutableP2PDir(), 'dhncentral.xml'))
    src = dhnio._read_data(os.path.join(dhnio.getExecutableDir(), 'dhncentral.xml'))
    if src:
        if identitydb.update(settings.CentralID(), src):
            if success_func:
                success_func('')
            return
    d = immediatelyCaching(settings.CentralID())
    if success_func is not None:
        d.addCallback(success_func)
    if fail_func is not None:
        d.addErrback(fail_func)

def Clear(excludeList=None):
    identitydb.clear(excludeList)

def CacheLen():
    return identitydb.size()

def PrintID(url):
    identitydb.print_id(url)

def PrintCacheKeys():
    identitydb.print_keys()

def PrintAllInCache():
    identitydb.print_cache()

def HasKey(url):
    return identitydb.has_key(url)

def FromCache(url):
    return identitydb.get(url)

def Remove(url):
    return identitydb.remove(url)

def UpdateAfterChecking(url, xml_src):
    #dhnio.Dprint(12, 'identitycache.UpdateAfterChecking ' + url)
    return identitydb.update(url, xml_src)

def getPageSuccess(src, url):
    UpdateAfterChecking(url, src)
    return src

def getPageFail(x, url):
    dhnio.Dprint(6, "identitycache.getPageFail NETERROR in request to " + url)
    return x

def pageRequestTwisted(url):
    dhnio.Dprint(12, 'identitycache.pageRequestTwisted ' + url)
    d = dhnnet.getPageTwisted(url)
    d.addCallback(getPageSuccess, url)
    d.addErrback(getPageFail, url)
    return d

# Even if we have a copy in cache we are to try and read another one
def scheduleForCaching(url):
    return pageRequestTwisted(url)

def immediatelyCaching(url, success_func=None, fail_func=None):
    global _CachingTasks
    if _CachingTasks.has_key(url):
        return _CachingTasks[url]
    
    # dhnio.Dprint(12, 'identitycache.immediatelyCaching new task ' + url)
    
    def _getPageSuccess(src, url, res):
        global _CachingTasks
        _CachingTasks.pop(url)
        if UpdateAfterChecking(url, src):
            if success_func is not None:
                success_func(url+'\n'+src)
            res.callback(src)
        else:
            if fail_func is not None:
                fail_func(url+'\n'+src)
            res.errback(src)
        
    def _getPageFail(x, url, res):
        global _CachingTasks
        _CachingTasks.pop(url)
        if fail_func is not None:
            fail_func(x)
        res.errback(x)
        
    result = Deferred()
    d = dhnnet.getPageTwisted(url)
    d.addCallback(_getPageSuccess, url, result)
    d.addErrback(_getPageFail, url, result)
    
    _CachingTasks[url] = result
    
    return result



