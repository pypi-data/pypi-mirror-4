#
# Copyright 2010-2012 Corporation of Balclutha (http://www.balclutha.org)
# 
#                All Rights Reserved
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
#
# Corporation of Balclutha DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS
# SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS, IN NO EVENT SHALL Corporation of Balclutha BE LIABLE FOR
# ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
# WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE. 
#
import logging, transaction
from lbn.zenoss import packutils
from ZenPacks.lbn.Base import ZenPack as ZenPackBase
from Products.CMFCore.DirectoryView import registerDirectory

import setuphandlers
from config import *

logger = logging.getLogger(PROJECTNAME)
logger.info('Installing %s module' % PROJECTNAME)

registerDirectory(SKINS_DIR, GLOBALS)


class ZenPack(ZenPackBase):
    """ Zenoss eggy thing """
    packZProperties = [
        ('zZopeURI', 'http://admin:password@localhost:8080', 'string'),
        ]

    def install(self, pack):
        """
        Set the collector plugin
        """
        ZenPackBase.install(self, pack)
	setuphandlers.install(pack.zport, self)

def initialize(context):
    """ Zope Product """
    zport = packutils.zentinel(context)
    if zport and not packutils.hasZenPack(zport, __name__):
        logger.info('Installing into ZenPackManager')
        transaction.begin()
	zpack = ZenPack(__name__)
        zoack = packutils.addZenPack(zport, zpack)
        transaction.commit()
    else:
        logger.info('Already in ZenPackManager')
        
