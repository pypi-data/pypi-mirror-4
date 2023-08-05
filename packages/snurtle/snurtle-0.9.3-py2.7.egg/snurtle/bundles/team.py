#!/usr/bin/env python
# Copyright (c) 2012 Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
from snurtle.cmd2      import options, make_option
from clibundle import CLIBundle

LIST_TEAM_TEMPLATE = '''<%objectid='{:<12}'.format(report['objectid'])
name='{:<45}'.format(report['name'])
if report['objectid'] == 10003:
    count='{:^8}'.format('-')
else:
    count='{:^8}'.format(len(report['memberObjectIds']))%>${objectid} ${name} ${count}'''

TEAM_TEMPLATE = '''    OGo#${report['objectid']} "${report['name']}"
    ================================================================= 
    Version: ${report['objectversion']}
    OwnerId: ${report['ownerobjectid']}'''

class TeamCLIBundle(CLIBundle):

    def do_list_teams(self, arg, opts=None):
        callid = self.server.search_for_objects(entity='Team', criteria='all', detail=128, callback=self.callback)
        response = self.get_response(callid)
        if response:
            self.set_result(response.payload, template=LIST_TEAM_TEMPLATE)

    @options([make_option('--objectid', type='int', help='objectId [Contact] to display.'),])
    def do_get_team(self, arg, opts=None):
        response = self._get_entity(opts.objectid, expected_type='Team', detail_level=65535)
        if response:
            self.set_result(response, template=TEAM_TEMPLATE)
