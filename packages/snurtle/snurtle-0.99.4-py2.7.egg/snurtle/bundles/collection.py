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
from snurtle.cmd2      import options, make_option
from clibundle import CLIBundle

class CollectionCLIBundle(CLIBundle):

    @options([make_option('--favorite', action='store_true',  help='List favorite collections.'),
              make_option('--kind', type='string',  help='List favorite projects.'),])
    def do_list_collections(self, arg, opts=None):
        '''List collections'''
        if opts.favorite:
            callid = self.server.get_favorites(entity_name='Collection', 
                                               detail_level=0, 
                                               callback=self.callback)
        else:
            callid = self.server.search_for_objects(entity='Collection',
                                                    criteria='list',
                                                    detail=0,
                                                    callback=self.callback)
        response = self.get_response(callid)
        if response:
            self.set_result(response)
                 
    @options( [ make_option('--objectid', type='int', 
                            help='ObjectId of Process entity to delete.'), ] )
    def do_delete_collection(self, arg, opts=None):
        '''Delete a collection.'''
        response = self._get_entity(opts.objectid, expected_type='Collection')
        if response:     
            callid = self.server.delete_object(objectid=opts.objectid,
                                                callback=self.callback)
            response = self.get_response(callid)
            if response:
                self.set_result(response)
                
    @options([make_option('--name',       type='string', help='Name for new collection.'),
              make_option('--projectid',  type='int',    help='Related Project Id'),
              make_option('--kind',       type='string', help='Kind strng'),
              make_option('--davenabled', action='store_true',  help='Should collection be available via WebDAV'),])
    def do_create_collection(self, arg, opts=None):
        values = { }
        if not opts.name:
            self.set_result('Collection title must be specified')
        values = { 'name': opts.name, 'objectid': 0, 'entityname': 'Collection' }
        if opts.projectid:   values['projectid'] = opts.projectid
        if opts.kind:        values['kind'] = opts.kind
        if opts.davenabled:  values['davenabled'] = True
        callid = self.server.put_object(values, callback=self.callback) 
        response = self.get_response(callid)       
        if response:
            self.set_result(response)
            
    @options([make_option('--objectid',     type='int', help='objectId of object to assign'),
              make_option('--collectionid', type='int', help='Collection to assign to'),])
    def do_collect(self, arg, opts=None):
        response = self._get_entity(opts.objectid)
        if response:
            values = { 'objectid':           0, 
                       'entityname':         'collectionAssignment', 
                       'collectionObjectId': opts.collectionid, 
                       'assignedObjectId':   opts.objectid }
            callid = self.server.put_object(values, callback=self.callback) 
            response = self.get_response(callid)       
            if response:
                self.set_result(response)
                
    @options([make_option('--objectid',     type='int', help='objectId of object to assign'),
              make_option('--collectionid', type='int', help='Collection to assign to'),])
    def do_uncollect(self, arg, opts=None):
        response = self._get_entity(opts.objectid)
        if response:
            values = { 'entityname':         'collectionAssignment', 
                       'collectionObjectId': opts.collectionid, 
                       'assignedObjectId':   opts.objectid }
            callid = self.server.delete_object(values, callback=self.callback) 
            response = self.get_response(callid)       
            if response:
                self.set_result(response)

    @options([make_option('--collectionid', type='int', help='Collection to assign to'),])              
    def do_list_collected(self, arg, opts=None):
        response = self._get_entity(opts.collectionid, expected_type='Collection', detail_level=65535)
        if response:
            object_ids = [ ]
            for entry in response.payload['_membership']:
                object_ids.append(entry['assignedobjectid'])
            callid = self.server.get_objects_by_id(fetchids=object_ids, callback=self.callback)
            response = self.get_response(callid)
            if response:
                self.set_result(response)
            

