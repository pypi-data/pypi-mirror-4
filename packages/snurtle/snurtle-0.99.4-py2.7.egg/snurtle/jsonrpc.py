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
import httplib, base64, json, uuid, urlparse

CLIENT_AGENT = 'snurtle-json-rpc/1.0 OpenGroupware Rocks!'

class JSONRPCClient(object):

    def __init__(self, uri, credentials=None):
      self._uri = uri
      self._online = False
      if credentials:
          self._creds = credentials
      else:
          self._creds = None

    @property
    def account(self):
        return self._account

    def test(self):
        try:
            self._account = self.call('getLoginAccount', [65535], uuid.uuid4().hex)
        except Exception as e:
            print e
            return False
        self._online = True
        return True

    @property
    def online(self):
        return self._online

    def call(self, method, parameters, call_id):
        # TODO: verify method is a string
        # TODO: verify parameters is a list
        
        REQUEST = { 'version': '1.1',
                    'method': method,
                    'id': call_id,
                    'params': parameters }
         
        PAYLOAD = json.dumps(REQUEST)
        connection = httplib.HTTPConnection(urlparse.urlparse(self._uri).netloc)
        connection.putrequest('POST', urlparse.urlparse(self._uri).path)
        
        if self._creds:
            coin = '{0}:{1}'.format(self._creds.get('username', ''),
                                    self._creds.get('password', ''))
            coin = 'Basic {0}'.format(base64.encodestring(coin)[:-1])
            connection.putheader('Authorization', coin)
            
        connection.putheader('User-Agent', CLIENT_AGENT)
        connection.putheader('Content-Length', str(len(PAYLOAD)))
        connection.putheader('Content-Type', 'application/json')
        connection.endheaders()
        connection.send(PAYLOAD)
        response = connection.getresponse()
        if response.status == 200:
            try:
                data = response.read()
                connection.close()
            except:
                pass
                # Do something clever
            else:
                data = json.loads(data)
                if data['error']:
                    print 'ERROR: {0}'.format(data['error'])
                    pass
                else:
                    return data['result']
        raise Exception("RPC Oops! HTTP Response Code#{0}".format(response.status))

