#!/usr/bin/python
#identitydb.py

import os
import dhnio
import settings
import identity
import nameurl

# Dictionary cache of identities - lookup by primary url
# global dictionary of identities in this file
# indexed with urls and contains identity objects
IdentityCache={}

#------------------------------------------------------------------------------ 

def init():
    dhnio.Dprint(4,"identitydb.init")
    iddir = settings.IdentityCacheDir()
    if not os.path.exists(iddir):
        dhnio.Dprint(8, 'identitydb.init create folder ' + iddir)
        dhnio._dir_make(iddir)

def clear(exclude_list=None):
    global IdentityCache
    dhnio.Dprint(4,"identitydb.clear")
    IdentityCache.clear()

    iddir = settings.IdentityCacheDir()
    if not os.path.exists(iddir):
        return

    for name in os.listdir(iddir):
        path = os.path.join(iddir, name)
        if not os.access(path, os.W_OK):
            continue
        if exclude_list:
            idurl = nameurl.FilenameUrl(name)
            if idurl in exclude_list:
                continue 
        os.remove(path)
        dhnio.Dprint(6, 'identitydb.clear remove ' + path)

def size():
    global IdentityCache
    clen = len(IdentityCache)
##    print "CacheLen is ", clen
    return(clen)

def has_key(url):
    global IdentityCache
    return(IdentityCache.has_key(url))

def idset(url, id_obj):
    global IdentityCache
    #dhnio.Dprint(14, 'identitydb.set ' + url)
    IdentityCache[url] = id_obj

def idget(url):
    global IdentityCache
    return IdentityCache.get(url, None)

def idremove(url):
    global IdentityCache
    #dhnio.Dprint(14,"identitydb.remove")
    IdentityCache.pop(url, None)

def get(url):
#    dhnio.Dprint(14, "identitydb.get " + str(url))
    if has_key(url):
        return idget(url)
    else:
        try:
            partfilename = nameurl.UrlFilename(url)
        except:
            dhnio.Dprint(1, "identitydb.get ERROR %s is incorrect" % str(url))
            return None
        filename = os.path.join(settings.IdentityCacheDir(), partfilename)
        if not os.path.exists(filename):
            dhnio.Dprint(6, "identitydb.get file %s not exist" % os.path.basename(filename))
            return None
        idxml = dhnio.ReadTextFile(filename)
        if idxml:
            idobj = identity.identity(xmlsrc=idxml)
            url2 = idobj.getIDURL()
            if url == url2:
                idset(url, idobj)
                return idobj
            else:
                dhnio.Dprint(1, "identitydb.get ERROR url=%s url2=%s" % (url, url2))
                return None

        dhnio.Dprint(6, "identitydb.get %s not found" % nameurl.GetName(url))
        return None

def update(url, xml_src):
    #dhnio.Dprint(14, 'identitydb.update: ' + url)
    try:
        newid = identity.identity(xmlsrc=xml_src)
    except:
        dhnio.DprintException()
        return False

    if not newid.isCorrect():
        dhnio.Dprint(1, "identitydb.update ERROR: incorrect identity " + str(url))
        return False

    try:
        if not newid.Valid():
            dhnio.Dprint(1, "identitydb.update ERROR identity not Valid" + str(url))
            return False
    except:
        dhnio.DprintException()
        return False

    filename=os.path.join(settings.IdentityCacheDir(), nameurl.UrlFilename(url))
    #dhnio.Dprint(14, "identitydb.update filename=" + filename)
    if os.path.exists(filename):
        oldidentityxml = dhnio.ReadTextFile(filename)
        oldidentity = identity.identity(xmlsrc=oldidentityxml)

        if oldidentity.publickey != newid.publickey:
            dhnio.Dprint(1, "identitydb.update ERROR new publickey does not match old : SECURITY VIOLATION " + url)
            return False

        if oldidentity.signature != newid.signature:
            dhnio.Dprint(6, 'identitydb.update have new data for ' + nameurl.GetName(url))
        else:
##            dhnio.Dprint(10, 'identitydb.update no changes for ' + url)
            idset(url, newid)
##            IdentityCache[url] = newid
            return True

    # PREPRO need to check that date or version is after old one so not vulnerable to replay attacks
    # PREPRO should be misc.AtomicWrite
    # dhnio.Dprint(6, "identitydb.update %s write to file %s" % (nameurl.GetName(url), filename))
    dhnio.WriteFile(filename, xml_src)             # publickeys match so we can update it
##    IdentityCache[url] = newid                       # add to IdentityCache
    idset(url, newid)

    return True

def remove(url):
    filename = os.path.join(settings.IdentityCacheDir(), nameurl.UrlFilename(url))
    if os.path.isfile(filename):
        dhnio.Dprint(6, "identitydb.remove file %s" % filename)
        try:
            os.remove(filename)
        except:
            dhnio.DprintException()
    idremove(url)

#------------------------------------------------------------------------------ 

def print_id(url):
    if has_key(url):
##        print "has key"
##        idForKey = IdentityCache[url]
        idForKey = get(url)
        dhnio.Dprint(6, str(idForKey.sources) )
        dhnio.Dprint(6, str(idForKey.contacts ))
        dhnio.Dprint(6, str(idForKey.publickey ))
        dhnio.Dprint(6, str(idForKey.signature ))

def print_keys():
    global IdentityCache
    for key in IdentityCache.keys():
        dhnio.Dprint(6, key)
##    print "PrintCacheKeys"

def print_cache():
    global IdentityCache
##    print "PrintCacheKeys"
    for key in IdentityCache.keys():
        dhnio.Dprint(6, "---------------------" )
        print_id(key)









