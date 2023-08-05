##############################################################################
#
# Copyright (c) 2005-2012 Zope Foundation and Contributors.
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
import re

import ZODB.ActivityMonitor
import ZODB.interfaces
import zope.component
import zc.monitor

from App.config import getConfiguration


def getZCMonitorConfiguration():
    config = getConfiguration()
    if not hasattr(config, 'product_config'):
        return
    product_config = config.product_config
    if config is None:
        return
    return product_config.get('five.z2monitor', None)


def registerDB(db):
    dbname = db.database_name
    zope.component.provideUtility(db, ZODB.interfaces.IDatabase, name=dbname)


def initialize(opened_event):
    config = getZCMonitorConfiguration()
    if config is None:
        return
    registerDB(opened_event.database)
    for name, db in zope.component.getUtilitiesFor(ZODB.interfaces.IDatabase):
        if db.getActivityMonitor() is None:
            db.setActivityMonitor(ZODB.ActivityMonitor.ActivityMonitor())

    try:
        #being backwards compatible here and not passing address if not given
        port = int(config['port'])
        zc.monitor.start(port)
    except KeyError:
        #new style bind
        try:
            bind = config['bind']
            bind = bind.strip()
            m = re.match(r'^(?P<addr>\S+):(?P<port>\d+)$', bind)
            if m:
                #we have an address:port
                zc.monitor.start((m.group('addr'), int(m.group('port'))))
                return

            m = re.match(r'^(?P<port>\d+)$', bind)
            if m:
                #we have a port
                zc.monitor.start(int(m.group('port')))
                return

            #we'll consider everything else as a domain socket
            zc.monitor.start(bind)
        except KeyError:
            #no bind config no server
            pass
