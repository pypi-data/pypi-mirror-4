#!/usr/bin/env python

##
## This example uses ICircuitListener to monitor how many circuits have
## failed since the monitor started up. If this figure is more than 50%,
## a warning-level message is logged.
## 
## Like the :ref:`stream_circuit_logger.py` example, we also log all new
## circuits.
## 

import os
import sys
import stat
import random
import time

from twisted.internet import reactor, task, endpoints
from twisted.python import usage
from zope.interface import implements

import txtorcon

def done(*args):
    print "done"
    reactor.stop()

def setup(proto):
    print 'Connected to a Tor version %s' % proto.version
    d = proto.signal('NEWNYM')
    d.addBoth(done)

def setup_failed(arg):
    print "SETUP FAILED",arg
    print arg
    reactor.stop()

endpoint = None
try:
    ## FIXME more Pythonic to not check, and accept more exceptions?
    if os.stat('/var/run/tor/control').st_mode & (stat.S_IRGRP | stat.S_IRUSR | stat.S_IROTH):
        print "using control socket"
        endpoint = endpoints.UNIXClientEndpoint(reactor, "/var/run/tor/control")
except OSError:
    pass

if endpoint is None:
    endpoint = endpoints.TCP4ClientEndpoint(reactor, "localhost", 9051)

print "Connecting via", endpoint
d = txtorcon.build_tor_connection(endpoint, build_state=False)
d.addCallback(setup).addErrback(setup_failed)
reactor.run()
