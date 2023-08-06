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
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import pkg_resources
pkg_resources.get_distribution('ZenPacks.lbn.ZopeMonitor')

from Products.ZenTestCase.BaseTestCase import BaseTestCase
from Products.ZenRRD.tests.BaseParsersTestCase import Object
from Products.ZenRRD.CommandParser import ParsedResults
from ZenPacks.lbn.ZopeMonitor.parsers.Munin import Munin


class TestMuninParser(BaseTestCase):

    def setUp(self):
        self.cmd = Object()
        deviceConfig = Object()
        deviceConfig.device = 'localhost'
        self.cmd.deviceConfig = deviceConfig

        self.cmd.parser = "Munin"
        self.cmd.result = Object()
        self.cmd.result.exitCode = 2
        self.cmd.severity = 2
        self.cmd.command = "testMuninPlugin"
        self.cmd.eventKey = "muninKey"
        self.cmd.eventClass = "/Cmd"
        self.cmd.component = "zencommand"
        self.parser = Munin()
        self.results = ParsedResults()
        self.dpdata = dict(processName='someJob a b c',
                           ignoreParams=False,
                           alertOnRestart=True,
                           failSeverity=3)

    def testGood(self):
        p1 = Object()
        p1.id = 'total_objs'
        p1.data = self.dpdata

        p2 = Object()
        p2.id = 'total_objs_memory'
        p2.data = self.dpdata

        p3 = Object()
        p3.id = 'target_number'
        p3.data = self.dpdata

        self.cmd.points = [p1, p2, p3]

        self.cmd.result.output = """total_objs:1487516.0
total_objs_memory:9657.0
target_number:25000.0"""
        self.parser.processResults(self.cmd, self.results)
        self.assertEquals( len(self.results.values), 3)
        self.assertEquals('total_objs',  self.results.values[0][0].id)
        self.assertEquals(1487516.0,  self.results.values[0][1])



if __name__ == '__main__':
    framework()
else:
    def test_suite():
        from unittest import TestSuite, makeSuite
        suite = TestSuite()
        suite.addTest(makeSuite(TestMuninParser))
        return suite
