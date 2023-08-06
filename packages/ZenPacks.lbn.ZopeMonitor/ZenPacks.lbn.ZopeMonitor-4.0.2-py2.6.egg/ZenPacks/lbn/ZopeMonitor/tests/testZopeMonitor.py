#
# Copyright 2010-2013 Corporation of Balclutha (http://www.balclutha.org)
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

from Products.ZenTestCase.BaseTestCase import BaseTestCase

#import pkg_resources
#pkg_resources.get_distribution('ZenPacks.lbn.ZopeMonitor')

import ZenPacks.lbn.ZopeMonitor

class TestZopeMonitor(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)


    def testEventsSetup(self):
        self.failUnless(self.dmd.Events.Status.Zope)

    def testTemplatesSetup(self):
        self.failUnless(self.dmd.Devices.Server.rrdTemplates.ZopeServer)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestZopeMonitor))
    return suite
