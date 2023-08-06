#
# Copyright 2010 Corporation of Balclutha (http://www.balclutha.org)
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
import re, logging
from Products.ZenUtils.Utils import getExitMessage
from Products.ZenRRD.CommandParser import CommandParser

DELIMITERS=""" :""" # presently space and colon

MuninParser = re.compile(r"""(\w+)([%s])([-0-9.]+)""" % DELIMITERS)

log = logging.getLogger('Munin')

class Munin(CommandParser):
    
    def __init__(self, *args, **kw):
        log.debug('Instantiating Munin Parser')

    def processResults(self, cmd, results):

        dps = {}

        output = cmd.result.output

        firstline = output.split('\n')[0].strip()
        exitCode = cmd.result.exitCode
        severity = cmd.severity
        if MuninParser.search(firstline):
            msg, values = '', output
        else:
            msg, values = output, ''

        msg = msg.strip() or 'Cmd: %s - Code: %s - Msg: %s' % (
            cmd.command, exitCode, getExitMessage(exitCode))

        if exitCode != 0:
            results.events.append(dict(device=cmd.deviceConfig.device,
                                       summary=msg,
                                       severity=severity,
                                       message=msg,
                                       performanceData=values,
                                       eventKey=cmd.eventKey,
                                       eventClass=cmd.eventClass,
                                       component=cmd.component))

        for line in cmd.result.output.split('\n'):
            match = MuninParser.search(line)
            if match:
                tag, delimiter, value = match.groups()
                dps[tag] = float(value)

        for dp in cmd.points:
            if dps.has_key(dp.id):
                results.values.append( (dp, dps[dp.id]) )

        
