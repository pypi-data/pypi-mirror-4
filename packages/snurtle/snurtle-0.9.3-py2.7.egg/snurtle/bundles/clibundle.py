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
#
from snurtle.cmd2 import options, make_option

class CLIBundle(object):

    def _get_entity(self, objectid, expected_type=None, detail_level=0):
        callid = self.server.get_object_by_id( fetchid = objectid,
                                               detail = detail_level,
                                               callback = self.callback,
                                               feedback = self.pfeedback )
        response = self.get_response(callid)
        if not response:
            self.set_result('No response from server before timeout', error=True)
            return False
        if isinstance(response.payload, dict):
            if expected_type:
                if response.payload['entityname'] != expected_type:
                    self.set_result('Specified object is not a "{0}", is a "{1}"'.format(expected_type, response.payload['entityname']), error=True)
                    return False
            return response
        self.set_result(response)
        return False

