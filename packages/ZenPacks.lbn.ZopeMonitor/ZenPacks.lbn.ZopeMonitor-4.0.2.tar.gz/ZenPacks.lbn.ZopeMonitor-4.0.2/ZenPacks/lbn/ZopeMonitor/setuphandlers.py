#
# Copyright 2010-2012 Corporation of Balclutha (http://www.balclutha.org)
# 
#                All Rights Reserved
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
#
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
import logging
from Acquisition import aq_base
from config import PROJECTNAME, MUNIN_THREADS, MUNIN_CACHE, MUNIN_ZODB, MUNIN_MEMORY
from lbn.zenoss.packutils import addZenPackObjects
from Products.ZenEvents.EventClass import manage_addEventClass
from Products.ZenModel.RRDTemplate import manage_addRRDTemplate

from datasources import ZopeThreadsDataSource, ZopeMemoryDataSource, ZopeCacheDataSource, ZopeDBActivityDataSource

logger = logging.getLogger(PROJECTNAME)
info = logger.info

def setDataPoints(graphdef, prefix, tags):
    pretty_tags = {}
    for tag in tags:
        if tag.find('_') != -1:
            pretty = tag.replace('_', ' ').capitalize()
        else:
            pretty = tag
        pretty_tags[pretty] = tag

    graphdef.manage_addDataPointGraphPoints(pretty_tags.keys())
    for dp in graphdef.graphPoints():
        dp.dpName = '%s_%s' % (prefix, pretty_tags[dp.getId()])

    info('added graph %s, datapoints(%s)' % (graphdef.getId(), ', '.join(pretty_tags.keys())))

def install(zport, zenpack):
    """
    Set the collector plugin
    """
    dmd = zport.dmd

    if not getattr(aq_base(dmd.Events.Status), 'Zope', None):
        manage_addEventClass(dmd.Events.Status, 'Zope')

    tpls = dmd.Devices.Server.rrdTemplates

    if getattr(aq_base(tpls), 'ZopeServer', None) is None:
        manage_addRRDTemplate(tpls, 'ZopeServer')
        tpl = tpls.ZopeServer

        tpl.manage_changeProperties(description='Monitors Zope Servers',
                                    targetPythonClass='Products.ZenModel.Device')
                                
        tpl.manage_addRRDDataSource('zopethreads', 'ZopeThreadsDataSource.ZopeThreadsDataSource')
        tpl.manage_addRRDDataSource('zopecache', 'ZopeCacheDataSource.ZopeCacheDataSource')
        tpl.manage_addRRDDataSource('zodbactivity', 'ZopeDBActivityDataSource.ZopeDBActivitySource')
        tpl.manage_addRRDDataSource('zopememory', 'ZopeMemoryDataSource.ZopeMemoryDataSource')

        info('added DataSources: zopethreads, zopecache, zodbactivity, zopememory')

        dst = tpl.datasources.zopethreads
        map(lambda x: dst.manage_addRRDDataPoint(x), MUNIN_THREADS)
        gdt = dst.manage_addGraphDefinition('Zope Threads')
        setDataPoints(gdt, 'zopethreads', MUNIN_THREADS)
        
        dsc = tpl.datasources.zopecache
        map(lambda x: dsc.manage_addRRDDataPoint(x), MUNIN_CACHE)
        gdc = dsc.manage_addGraphDefinition('Zope Cache')
        setDataPoints(gdc, 'zopecache', MUNIN_CACHE)

        dsd = tpl.datasources.zodbactivity
        map(lambda x: dsd.manage_addRRDDataPoint(x), MUNIN_ZODB)
        gdd = dsd.manage_addGraphDefinition('ZODB Activity')
        setDataPoints(gdd, 'zodbactivity', MUNIN_ZODB)

        dsm = tpl.datasources.zopememory
        map(lambda x: dsm.manage_addRRDDataPoint(x), MUNIN_MEMORY)
        gdm = dsm.zopememory.manage_addGraphDefinition('Zope Memory')
        setDataPoints(gdm, 'zopememory', MUNIN_MEMORY)

    addZenPackObjects(zenpack, (zport.dmd.Events.Status.Zope, tpls.ZopeServer))


def uninstall(zport):
    
    for parent, id in ((zport.dmd.Events.Status, 'Zope'),
                       (zport.dmd.Devices.Server.rrdTemplates, 'ZopeServer')):
        if getattr(aq_base(parent), id, None):
            parent._delObject(id)
                       
