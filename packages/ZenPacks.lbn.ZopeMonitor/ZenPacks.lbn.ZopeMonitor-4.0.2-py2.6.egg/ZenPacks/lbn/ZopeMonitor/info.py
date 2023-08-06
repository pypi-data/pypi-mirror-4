#
# Copyright 2012 Corporation of Balclutha (http://www.balclutha.org)
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

from zope.interface import implements
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.infos.template import BasicDataSourceInfo

from interfaces import IZopeThreadsDataSourceInfo, IZopeDBActivityDataSourceInfo, \
    IZopeMemoryDataSourceInfo, IZopeCacheDataSourceInfo


class ZopeDataSourceInfo(BasicDataSourceInfo):

    zopeURI = ProxyProperty('zopeURI')
    timeout = ProxyProperty('timeout')

    @property
    def testable(self):
        """
        We can NOT test this datsource against a specific device
        """
        return False


class ZopeCacheDataSourceInfo(ZopeDataSourceInfo):
    implements(IZopeCacheDataSourceInfo)

class ZopeDBActivityDataSourceInfo(ZopeDataSourceInfo):
    implements(IZopeDBActivityDataSourceInfo)

class ZopeMemoryDataSourceInfo(ZopeDataSourceInfo):
    implements(IZopeMemoryDataSourceInfo)

class ZopeThreadsDataSourceInfo(ZopeDataSourceInfo):
    implements(IZopeThreadsDataSourceInfo)
