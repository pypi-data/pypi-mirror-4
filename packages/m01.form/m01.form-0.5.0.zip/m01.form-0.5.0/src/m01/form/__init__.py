##############################################################################
#
# Copyright (c) 2009 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import time
import struct
import threading
import zope.component

import bson.objectid

from m01.mongo import interfaces

LOCAL = threading.local()


def getMongoDBConnection(name):
    """Returns a mongodb connection"""
    pool = zope.component.getUtility(interfaces.IMongoConnectionPool,
        name=name)
    return pool.connection


def clearThreadLocalCache(event=None):
    """A subscriber to EndRequestEvent

    Cleans up the thread local cache on each end request.
    """
    for key in LOCAL.__dict__.keys():
        del LOCAL.__dict__[key]


def getObjectId(counter=0):
    """Knows how to generate similar ObjectId based on integer (counter)
    
    Note: this method can get used if you need to define similar ObjectId
    in a non persistent environment if need to bootstrap mongo containers.
    """
    # not every system can generate timestamps from 0 (zero) seconds
    secs = 60*60
    secs += counter
    time_tuple = time.gmtime(secs)
    ts = time.mktime(time_tuple)
    oid = struct.pack(">i", int(ts)) + "\x00" * 8
    return bson.objectid.ObjectId(oid)
