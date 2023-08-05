#!/usr/bin/env python
# Copyright (c) 2012 
#  Adam Tauno Williams <awilliam@whitemice.org>
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
from snurtle.cmd2      import options, make_option
from clibundle import CLIBundle

TIME_TEMPLATE = '''UTC: ${report['gmttime']} User: ${report['usertime']} @ ${report['offsettimezone']} isDST: ${report['isdst']}''' 

LOCK_TEMPLATE = '''token#${report['token']} target: "${report['targetObjectId']}" 
    operations: ${report['operations']} exclusive: ${report['exclusive']} granted: ${report['granted']} expires: ${report['expires']}'''
    
ACL_TEMPLATE = '''ACL (${report['targetentityname']}, ${report['targetobjectid']}) = (${report['action']}, ${report['operations']})'''

PROP_LIST_TEMPLATE='''${report['propertyName']} = ${report['value']}'''

PERFORMANCE_TEMPLATE='''${report['command']} Count:${report['counter']} Errors:${report['errors']} Max:${report['max']} Min:${report['min']} Total:${report['total']}'''
    
class CommonCLIBundle(CLIBundle):
        
    @options([make_option('--objectid', type='int', help='objectId of entity on which to set property.'),])
    def do_list_properties(self, arg, opts=None):
        """List object properties attached to an object."""
        response = self._get_entity(opts.objectid, detail_level=16)
        if response:
            self.set_result(response.payload['_properties'], template=PROP_LIST_TEMPLATE)
            
    @options([make_option('--objectid', type='int', help='objectId of entity on which to set property.'),])
    def do_get_time(self, arg, opts=None):
        """List object properties attached to an object."""
        callid = self.server.search_for_objects(entity='time', criteria='', detail=0, callback=self.callback)
        response = self.get_response(callid)
        if response:
            self.set_result(response.payload, template=TIME_TEMPLATE)            
        
    @options([make_option('--objectid', type='int', help='objectId of entity on which to set property.'),
              make_option('--namespace', type='string', help='Namespace of the ObjectProperty'),
              make_option('--attribute', type='string', help='Attribute name'),
              make_option('--value', help='ObjectProperty value')])          
    def do_set_property(self, arg, opts=None):
        """Set, or create, the specified object property."""
        response = self._get_entity(opts.objectid)
        if response:
            prop = { 'entityName':     'objectProperty',
                     'parentobjectid': opts.objectid,
                     'namespace':      opts.namespace,
                     'attribute':      opts.attribute,
                     'value':          opts.value }
            callid = self.server.put_object( payload = prop, callback = self.callback )
            response = self.get_response(callid)
            if response:
                self.set_result(response)
                
    @options([make_option('--objectid', type='int', help='objectId of entity on which to set property.'),
              make_option('--namespace', type='string', help='Namespace of the ObjectProperty'),
              make_option('--attribute', type='string', help='Attribute name'), ] )          
    def do_delete_property(self, arg, opts=None):
        """Delete the specified object property."""
        response = self._get_entity(opts.objectid)
        if response:
            prop = { 'entityName':     'objectProperty',
                     'parentobjectid': opts.objectid,
                     'namespace':      opts.namespace,
                     'attribute':      opts.attribute }
            callid = self.server.delete_object( payload = prop, callback = self.callback )
            response = self.get_response(callid)
            if response:
                self.set_result(response)                
            
    @options([make_option('--objectid', type='int', help='objectId of object to favorite.'), ] )          
    def do_favorite(self, arg, opts=None):
        """Attach favorite status to the specified object."""
        response = self._get_entity(opts.objectid)
        if response:
            callid = self.server.favorite(objectids=[opts.objectid], callback = self.callback)
            response = self.get_response(callid)
            if response:
                self.set_result(response)
        else:
            #TODO: Do something here?
            pass

    @options([make_option('--objectid', type='int', help='objectId of object to unfavorite.'), ] )          
    def do_unfavorite(self, arg, opts=None):
        """Remove favorite status from the specified object."""
        callid = self.server.unfavorite(objectids=[opts.objectid], callback = self.callback)
        response = self.get_response(callid)
        if response:
            self.set_result(response)
            
    @options([make_option('--objectid', type='int', help='objectId of object to delete.'), ] )          
    def do_delete_object(self, arg, opts=None):
        """Delete the specfied object."""
        response = self._get_entity(opts.objectid)
        if response:
            callid = self.server.delete_object(opts.objectid, callback=self.callback)
            response = self.get_response(callid)
            if response:
                self.set_result(response)

    @options([make_option('--objectid', type='int', help='objectId of object to identity.'), ] )          
    def do_get_type(self, arg, opts=None):
        """Retrieve the type of the specified object."""
        callid = self.server.get_type_of_object(fetchid=opts.objectid, callback=self.callback)
        response = self.get_response(callid)
        if response:
            self.set_result(response.payload)
                
    @options([make_option('--objectid', type='int', help='objectId of object.'), ] )          
    def do_list_acls(self, arg, opts=None):
        """List the ACLs for the specified object."""
        response = self._get_entity(opts.objectid, detail_level=32768)
        if response:
            if '_access' in response.payload:
                self.set_result(response.payload['_access'], template=ACL_TEMPLATE)
            else:
                self.set_result('Object retrieved does not support ACLs', error=True)
                
    @options([make_option('--objectid',  type='int', help='Object the ACL applies to.s'),
              make_option('--contextid', type='int', help='Context of ACL'),
              make_option('--allowed',   action='store_true', help='ACL allows the specified permissions [default].'),
              make_option('--denied',    action='store_true', help='ACL delies the specified permissions'),
              make_option('--write',     action='store_true', help='Apply write permission to ACL'),
              make_option('--read',      action='store_true', help='Apply read permission to ACL'), 
              make_option('--view',      action='store_true', help='Apply view permission to ACL'), 
              make_option('--list',      action='store_true', help='Apply list permission to ACL'), 
              make_option('--delete',    action='store_true', help='Apply delete permission to ACL'), 
              make_option('--insert',    action='store_true', help='Apply insert permission to ACL'),
              make_option('--admin',     action='store_true', help='Apply admin permission to ACL'), ] )          
    def do_set_acl(self, arg, opts=None):
        """Ceate or modify an ACL on the specified object."""
        if not opts.objectid:
            self.set_result('"objectid" parameter is mandatory.', error=True)
            return
        if not opts.contextid:
            self.set_result('"contextid" parameter is mandatory.', error=True)  
        response = self._get_entity(opts.objectid, detail_level=32768)
        if response:
            permissions = [ ]
            if opts.write:  permissions.append('w')
            if opts.read:   permissions.append('r')
            if opts.view:   permissions.append('v')
            if opts.list:   permissions.append('l')
            if opts.delete: permissions.append('d')
            if opts.insert: permissions.append('i')
            if opts.admin:  permissions.append('a')
            payload = { 'parentObjectId': opts.objectid, 
                        'entityName':     'acl',
                        'targetObjectId': opts.contextid,
                        'operations':     ''.join(permissions) }
            if opts.denied:
               payload['action'] = 'denied'
            else:
               payload['action'] = 'allowed'
            callid = self.server.put_object(payload, callback=self.callback)
            response = self.get_response(callid)
            if response:
                self.set_result(response, template=ACL_TEMPLATE)
                
    @options([make_option('--objectid',  type='int', help='Object to lock.'),
              make_option('--duration',  type='int', default=3600, help='Duration of the lock in seconds'),
              make_option('--exclusive', action='store_true', help='Request lock be exlucsive.'),
              make_option('--write',     action='store_true', help='Lock against write operations'),
              make_option('--run',       action='store_true', help='Lock against run operations'), 
              make_option('--delete',    action='store_true', help='Lock against delete operations'), ] )          
    def do_lock(self, arg, opts=None):
        """Acquire or refresh a lock on the specified entity."""
        operations = ' '
        if opts.write:  operations += 'w'
        if opts.run:    operations += 'x'
        if opts.delete: operations += 'd'
        e = { 'targetObjectId': opts.objectid, 
              'entityName':     'lock',
              'duration':       opts.duration,
              'exclusive':      'NO',
              'operations':     operations }
        if opts.exclusive: e[ 'exclusive' ] = 'YES'
        callid = self.server.put_object(e, callback=self.callback)
        response = self.get_response(callid)
        if response:
            self.set_result(response, template=LOCK_TEMPLATE)
            
    @options( [ make_option( '--objectid', type='int', help='Object to unlock'), 
                make_option( '--token', type='string', default='', help='Token of lock to release [NOT IMPLEMENTED]'),] )
    def do_unlock(self, arg, opts=None):
        """Remove locks on the specified object."""
        callid = self.server.delete_object( { 'entityName': 'lock',
                                              'targetObjectId': opts.objectid },
                                              callback=self.callback )
        response = self.get_response( callid )
        if response:
            self.set_result(response, template=LOCK_TEMPLATE)
            
    @options( [ make_option( '--objectid', type='int', help='Object to retrieve locking information on'), ] )
    def do_list_locks(self, arg, opts=None):
        """List the locks on the specified object."""
        callid = self.server.search_for_objects( 'lock', { 'targetObjectId': opts.objectid }, detail=0, callback=self.callback )
        response = self.get_response( callid )
        if response:
            self.set_result(response, template=LOCK_TEMPLATE) 
            
    @options( [ make_option('--logic', action='store_true', help="Return Logic performance statistics" ), ] )
    def do_get_performance(self, arg, opts=None):
        """Return server performance information."""
        callid = self.server.get_performance( 'logic', callback=self.callback )
        response = self.get_response( callid )
        if response:
            self.set_result( response, template=PERFORMANCE_TEMPLATE ) 
