#
# Copyright 2010 Corporation of Balclutha (http://www.balclutha.org)
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
from DataSourceBase import DataSourceBase
from ZenPacks.lbn.ZopeMonitor.config import MUNIN_THREADS

class ZopeThreadsDataSource(DataSourceBase):
    """Zope Threads""" 
    meta_type = 'ZopeThreadsDataSource'

    munin_tags = MUNIN_THREADS

    uri = 'zopethreads'

