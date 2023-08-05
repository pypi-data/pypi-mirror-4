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

PROJECT_TEMPLATE = '''
  objectId#${report['objectid']} version: ${report['version']} status: ${report['status']} 
    placeHolder: ${report['placeholder']} ownerId: ${report['ownerobjectid']}
    =================================================================
    name:           "${report['name']}" 
    number:         "${report['number']}" 
    parentObjectId: "${report['parentobjectid']}"
    folderObjectId  "${report['folderobjectid']}"
    startDate:      "${report['startdate']}"
    --enterprises--
    %if len(report['_enterprises']) == 0:
      No enterprises are assigned to project.
    %else:
      %for assignment in report['_enterprises']:
      ${assignment['targetobjectid']}
      %endfor
    %endif
    --projects--
    %if len(report['_contacts']) == 0:
      No contacts are assigned to project..
    %else:
      %for assignment in report['_contacts']:
      ${assignment['targetobjectid']}
      %endfor
    %endif    
'''

class ProjectCLIBundle(CLIBundle):


    @options([make_option('--favorite', action='store_true',  help='List favorite projects.'),
              make_option('--name', type='string',  help='List favorite projects.'),])
    def do_list_projects(self, arg, opts=None):
        if opts.favorite:
            callid = self.server.get_favorites(entity_name='Project', 
                                               detail_level=0, 
                                               callback=self.callback)
        elif opts.name:
            callid = self.server.search_for_objects(entity='Project', 
                                                    criteria={ 'conjunction': 'AND', 'name': opts.name },
                                                    detail=0, 
                                                    callback=self.callback)        
        else:
            callid = self.server.search_for_objects(entity='Project',
                                                    criteria='list',
                                                    detail=16,
                                                    callback=self.callback)
        response = self.get_response(callid)
        if response:
            self.set_result(response)
                
    @options([make_option('--projectid', type='int', 
                  help='objectId [Project] to reparent.'),
              make_option('--parentid', type='int', 
                  help='objectId [Project] of new parent, or zero to remove parent.')])          
    def do_reparent_project(self, arg, opts=None):
        response = self._get_entity(opts.projectid, expected_type='Project')
        if response:
            project = response.payload  
            if opts.parentid:
                parent = self._get_entity(opts.parentid, expected_type='Project')
                if parent:
                    parentid = parent.payload['objectid']
                else:
                    return
            else:
                parentid = None    
            project['parentprojectid'] = parentid
            callid = self.server.put_object( payload = project,
                                             callback = self.callback )
            response = self.get_response(callid)
            if response:
                self.set_result(response)
            else:
                self.set_result('Specified parent is not a project.')


    @options([make_option('--parentid', type='int',     help='List favorite projects.'),
              make_option('--name',     type='string',  help='List favorite projects.'),
              make_option('--number',   type='string',  help=''),
              make_option('--kind',     type='string',  help=''),
              make_option('--url',      type='string',  help=''),
              make_option('--isfake',   action='store_true',  help=''),])
    def do_create_project(self, arg, opts=None):
        values = { }
        if not opts.name:
            self.set_result('Project name must be specified', error=True)
        values = { 'name': opts.name, 'objectid': 0, 'entityname': 'Project' }
        if opts.number:   values['number'] = opts.number
        if opts.kind:     values['kind'] = opts.kind
        if opts.parentid: values['parentobjectid'] = opts.parentid
        if opts.url:      values['url'] = opts.url
        if opts.isfake:   values['placeholder'] = 1
        callid = self.server.put_object(values, callback=self.callback) 
        response = self.get_response(callid)       
        if response:
            self.set_result(response)
            
    @options([make_option('--objectid', type='int', help='objectId [Project] to display.'),])
    def do_get_project(self, arg, opts=None):
        response = self._get_entity(opts.objectid, expected_type='Project', detail_level=65535)
        if response:
            self.set_result(response, template=PROJECT_TEMPLATE)
