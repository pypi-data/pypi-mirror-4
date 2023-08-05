#!/usr/bin/python
#webtraffic.py
#
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2012
#    Use of this software constitutes acceptance of the Terms of Use
#      http://datahaven.net/terms_of_use.html
#    All rights reserved.
#
#

import sys

try:
    from twisted.internet import reactor
except:
    sys.exit('Error initializing twisted.internet.reactor in trafficstats.py')

from twisted.web import server, resource


#-------------------------------------------------------------------------------


#(total bytes, finished packets, failed packets, total packets)
_InboxPacketsCount = 0
_InboxByIDURL = {}
_InboxByHost = {}
_InboxByProto = {}

_OutboxPacketsCount = 0
_OutboxByIDURL = {}
_OutboxByHost = {}
_OutboxByProto = {}

_WebListener = None

_DefaultReloadTimeout = 600

#-------------------------------------------------------------------------------


def inbox(newpacket, proto, host_, status):
    global _InboxPacketsCount
    global _InboxByIDURL
    global _InboxByHost
    global _InboxByProto

    if newpacket is None:
        return

    bytes = len(newpacket)
    idurl = newpacket.CreatorID
    try:
        host = host_.split(':')[0]
    except:
        host = host_

    if not _InboxByIDURL.has_key(idurl):
        _InboxByIDURL[idurl] = [0, 0, 0, 0]
    _InboxByIDURL[idurl][0] += bytes
    if status == 'finished':
        _InboxByIDURL[idurl][1] += 1
    else:
        _InboxByIDURL[idurl][2] += 1
    _InboxByIDURL[idurl][3] += 1

    if not _InboxByHost.has_key(host):
        _InboxByHost[host] = [0, 0, 0, 0]
    _InboxByHost[host][0] += bytes
    if status == 'finished':
        _InboxByHost[host][1] += 1
    else:
        _InboxByHost[host][2] += 1
    _InboxByHost[host][3] += 1

    if not _InboxByProto.has_key(proto):
        _InboxByProto[proto] = [0, 0, 0, 0]
    _InboxByProto[proto][0] += bytes
    if status == 'finished':
        _InboxByProto[proto][1] += 1
    else:
        _InboxByProto[proto][2] += 1
    _InboxByProto[proto][3] += 1

    _InboxPacketsCount += 1

def outbox(workitem, proto, host, status):
    global _OutboxPacketsCount
    global _OutboxByIDURL
    global _OutboxByHost
    global _OutboxByProto

    bytes = workitem.filesize
    idurl = workitem.remoteid

    if not _OutboxByIDURL.has_key(idurl):
        _OutboxByIDURL[idurl] = [0, 0, 0, 0]
    _OutboxByIDURL[idurl][0] += bytes
    if status == 'finished':
        _OutboxByIDURL[idurl][1] += 1
    else:
        _OutboxByIDURL[idurl][2] += 1
    _OutboxByIDURL[idurl][3] += 1

    if not _OutboxByHost.has_key(host):
        _OutboxByHost[host] = [0, 0, 0, 0]
    _OutboxByHost[host][0] += bytes
    if status == 'finished':
        _OutboxByHost[host][1] += 1
    else:
        _OutboxByHost[host][2] += 1
    _OutboxByHost[host][3] += 1

    if not _OutboxByProto.has_key(proto):
        _OutboxByProto[proto] = [0, 0, 0, 0]
    _OutboxByProto[proto][0] += bytes
    if status == 'finished':
        _OutboxByProto[proto][1] += 1
    else:
        _OutboxByProto[proto][2] += 1
    _OutboxByProto[proto][3] += 1

    _OutboxPacketsCount += 1

#-------------------------------------------------------------------------------

class TrafficPage(resource.Resource):
    header_html = '''<html><head>
<meta http-equiv="refresh" content="%(reload)s">
<title>Traffic</title></head>
<body bgcolor="#FFFFFF" text="#000000" link="#0000FF" vlink="#0000FF">
<form action="" method="get">
<input size="4" name="reload" value="%(reload)s" />
<input type="submit" value="update" />
</form>
<a href="?reload=1&type=%(type)s&dir=%(dir)s">[1 sec.]</a>|
<a href="?reload=5&type=%(type)s&dir=%(dir)s">[5 sec.]</a>|
<a href="?reload=10&type=%(type)s&dir=%(dir)s">[10 sec.]</a>|
<a href="?reload=60&type=%(type)s&dir=%(dir)s">[60 sec.]</a>
<br>
<a href="?type=idurl&reload=%(reload)s&dir=%(dir)s">[by idurl]</a>|
<a href="?type=host&reload=%(reload)s&dir=%(dir)s">[by host]</a>|
<a href="?type=proto&reload=%(reload)s&dir=%(dir)s">[by proto]</a>
<br>
<a href="?type=%(type)s&reload=%(reload)s&dir=in">[income traffic]</a>|
<a href="?type=%(type)s&reload=%(reload)s&dir=out">[outgoing traffic]</a>
<br>
<table><tr>
<td align=left>%(type)s
<td>total bytes
<td>total packets
<td>finished packets
<td>failed packets
'''

    def __init__(self,parent):
        self.parent = parent
        resource.Resource.__init__(self)

    def render(self, request):
        global _InboxPacketsCount
        global _InboxByIDURL
        global _InboxByHost
        global _InboxByProto
        global _OutboxPacketsCount
        global _OutboxByIDURL
        global _OutboxByHost
        global _OutboxByProto

        direction = request.args.get('dir', [''])[0]
        if direction not in ('in', 'out'):
            direction = 'in'
        typ = request.args.get('type', [''])[0]
        if typ not in ('idurl', 'host', 'proto'):
            typ = 'idurl'
        reloadS = request.args.get('reload', [''])[0]
        try:
            reloadV = int(reloadS)
        except:
            reloadV = _DefaultReloadTimeout

        d = {'type': typ, 'reload': str(reloadV), 'dir': direction}
        out = self.header_html % d
        if direction == 'in':
            if typ == 'idurl':
                for i, v in _InboxByIDURL.items():
                    out += '<tr><td><a href="%s">%s</a><td>%d<td>%d<td>%d<td>%d\n' % (
                        i, i, v[0], v[3], v[1], v[2])
            elif typ == 'host':
                for i, v in _InboxByHost.items():
                    out += '<tr><td>%s<td>%d<td>%d<td>%d<td>%d\n' % (
                        i, v[0], v[3], v[1], v[2])
            elif typ == 'proto':
                for i, v in _InboxByProto.items():
                    out += '<tr><td>%s<td>%d<td>%d<td>%d<td>%d\n' % (
                        i, v[0], v[3], v[1], v[2])
        else:
            if typ == 'idurl':
                for i, v in _OutboxByIDURL.items():
                    out += '<tr><td><a href="%s">%s</a><td>%d<td>%d<td>%d<td>%d\n' % (
                        i, i, v[0], v[3], v[1], v[2])
            elif typ == 'host':
                for i, v in _OutboxByHost.items():
                    out += '<tr><td>%s<td>%d<td>%d<td>%d<td>%d\n' % (
                        i, v[0], v[3], v[1], v[2])
            elif typ == 'proto':
                for i, v in _OutboxByProto.items():
                    out += '<tr><td>%s<td>%d<td>%d<td>%d<td>%d\n' % (
                        i, v[0], v[3], v[1], v[2])

        out += '</table>'
        if direction == 'in':
            out += '<p>total income packets: %d</p>' % _InboxPacketsCount
        else:
            out += '<p>total outgoing packets: %d</p>' % _OutboxPacketsCount
        out += '</body></html>'

        return out


class RootResource(resource.Resource):
    def __init__(self):
        resource.Resource.__init__(self)
        logpage = TrafficPage(self)
        self.putChild('', logpage)

def init(port = 9997):
    global _WebListener
    if _WebListener:
        return
    root = RootResource()
    site = server.Site(root)
    try:
        _WebListener = reactor.listenTCP(port, site)
    except:
        pass

def shutdown():
    global _WebListener
    if _WebListener:
        _WebListener.stopListening()
        del _WebListener
        _WebListener = None

if __name__ == "__main__":
    init()
    reactor.run()

