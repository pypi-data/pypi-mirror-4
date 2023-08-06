#
#    Copyright 2010-2012 Corporation of Balclutha (http://www.balclutha.org)
# 
#                All Rights Reserved
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
import logging
from Products.ZenModel.ZenPack import ZenPack as ZenPackBase
from packutils import zentinel

logger = logging.getLogger('lbn.zenoss')


class ZenPack(ZenPackBase):
    """ Zenoss eggy thing - placeholder to shim if ever required """

def initialize(context):
    """
    function to hack zope instance upon startup
    """
    zport = zentinel(context)

    # purge any uninstalled ZenPacks
    if zport:
        mgr = zport.dmd.ZenPackManager
        broken = filter(lambda x: not hasattr(x, 'isBroken') or x.isBroken(), mgr.packs())
        if broken:
            ids = map(lambda x: mgr.getBrokenPackName(x), broken)
            logger.info('removing: %s' % ', '.join(ids))
            # hard-core ZODB removal ...
            # TODO - get this working ...
            for id in ids:
                try:
                    mgr.packs._delObject(id)
                except Exception, e:
                    log.error(str(e), exc_info=True)
#
# unilaterally apply monkeypatches to running Zope server
#
import monkeypatches
