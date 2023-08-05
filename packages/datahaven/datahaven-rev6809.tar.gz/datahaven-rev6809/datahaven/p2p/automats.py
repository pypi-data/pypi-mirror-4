#!/usr/bin/env python
#automats.py
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2012
#    All rights reserved.
#
#

import os
import sys

try:
    from twisted.internet import reactor
except:
    sys.exit('Error initializing twisted.internet.reactor in automats.py')
from twisted.internet.defer import Deferred, maybeDeferred
from twisted.internet.task import LoopingCall


import lib.dhnio as dhnio
import lib.dhnnet as dhnnet
import lib.misc as misc
import lib.nameurl as nameurl
import lib.packetid as packetid
import lib.settings as settings
import lib.contacts as contacts
import lib.transport_control as transport_control
import lib.diskusage as diskusage
import lib.automat as automat


import initializer
import p2p_connector

import dhninit
import identitypropagate
import install
import webcontrol

#------------------------------------------------------------------------------

_StatesDict = {
    'init at startup':           'beginning',
    'init local':                'local settings initialization',
    'init contacts':             'contacts initialization',
    'init connection':           'initializing connections',
    'init modules':              'starting modules',
    'init install':              'preparing install section',
    'network at startup':        'starting connection',
    'network stun':              'detecting external IP address',
    'network upnp':              'configuring UPnP',
    'network connected':         'internet connection is fine',
    'network disconnected':      'internet connection is not working',
    'network google?':           'is www.google.com available?',
    'p2p at startup':            'initial peer-to-peer state',
    'p2p transports':            'starting network transports',
    'p2p centralservice':        'connecting to central server',
    'p2p propagate':             'propagate my identity',
    'p2p incomming?':            'waiting response from others',
    'p2p connected':             'ready',
    'p2p disconnected':          'starting disconnected',
    'central at startup':        'starting central server connection',
    'central identity':          'sending my identity to central server',
    'central settings':          'sending my settings to central server',
    'central request settings':  'asking my settings from central server',
    'central suppliers':         'requesting suppliers from central server',
    'central connected':         'connected to central server',
    'central disconnected':      'disconnected from central server',
    }

_GlobalState = 'AT_STARTUP'
_GlobalStateNotifyFunc = None

#------------------------------------------------------------------------------

def set_global_state(st):
    global _GlobalState
    global _GlobalStateNotifyFunc
    oldstate = _GlobalState
    _GlobalState = st
    dhnio.Dprint(2, (' ' * 40) + '{%s}->{%s}' % (oldstate, _GlobalState))
    if _GlobalStateNotifyFunc is not None and oldstate != _GlobalState:
        try:
            _GlobalStateNotifyFunc(_GlobalState)
        except:
            dhnio.DprintException()


def get_global_state():
    global _GlobalState
    dhnio.Dprint(6, 'dhninit.get_global_state return [%s]' % _GlobalState)
    return _GlobalState


def get_global_state_label():
    global _GlobalState
    global _StatesDict
    return _StatesDict.get(_GlobalState.replace('_', ' ').lower(), '')


def get_automats_by_index():
    return automat.objects()


def SetGlobalStateNotifyFunc(f):
    global _GlobalStateNotifyFunc
    _GlobalStateNotifyFunc = f
    
def SetSingleStateNotifyFunc(f):
    automat.SetStateChangedCallback(f)

#------------------------------------------------------------------------------








