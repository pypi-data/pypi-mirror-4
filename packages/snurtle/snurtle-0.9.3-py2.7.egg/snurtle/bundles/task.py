#!/usr/bin/env python
# Copyright (c) 2011, 2012 Adam Tauno Williams <awilliam@whitemice.org>
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

TASK_LIST_TEMPLATE='''<%
  status = 'Unknown'
  if report[ 'status' ] == '00_created': status = 'Created'
  elif report[ 'status' ] == '02_rejected': status = 'Rejected'
  elif report[ 'status' ] == '20_processing': status = 'Processing'
  elif report[ 'status' ] == '25_done': status = 'Done' 
  elif report[ 'status' ] == '30_archived': status = 'Archived'  
%>${report['objectId']} ${report['name']} ${report['kind']} ${report['status']} ${report['start']} ${report['end']} '''

TASK_TEMPLATE='''<%
  status = 'Unknown'
  if report[ 'status' ] == '00_created': status = 'Created'
  elif report[ 'status' ] == '02_rejected': status = 'Rejected'
  elif report[ 'status' ] == '20_processing': status = 'Processing'
  elif report[ 'status' ] == '25_done': status = 'Done' 
  elif report[ 'status' ] == '30_archived': status = 'Archived'  
  projectid = report.get( 'objectprojectid', 'n/a' )
  projectname = report.get( 'projectname', 'n/a' )
%>objectId#${report['objectid']} version: ${report['version']} sensitivity: ${report['sensitivity']} parentId#${report['parenttaskobjectid']}
=================================================================
  Name:      "${report['name']}"
  Keywords:  "${report['keywords']}" 
  Kilometers: ${report['kilometers']} Total Work: ${report['totalwork']} 
  Start:      ${report['start']} End: ${report['end']} Completed: ${report['completiondate']}
  ExecutorId: ${report['executantobjectid']} CreatorId: ${report['creatorobjectid']} OwnerId: ${report['ownerobjectid']}
  
  Project:    ${projectid} "${projectname}"
  Status:     ${status}   Priority: ${report['priority']}   % Complete: ${report['percentcomplete']}
  Kind:       ${report['kind']}
  __Associated__
    Contacts:    ${report['associatedcontacts']}
    Enterprises: ${report['associatedCompanies']}
  Flags:   
     
__Properties__
%for prop in report['_properties']:
  ${prop['propertyName']} = ${prop['value']}
%endfor

__Comment__
${report['comment']}
    '''
    

class TaskCLIBundle(CLIBundle):

    #
    #  Tasks
    #
    
    def _task_action(self, objectid, action, comment):
        response = self._get_entity(objectid, expected_type='Task')
        if response:
            if action != 'comment':
                if action.upper() not in response.payload['flags']: 
                    self.set_result('Context not a candidate to {0} this task.'.\
                            format(action))
                    return False
            payload = { 'entityName':   'taskNotation',
                        'action':       action,
                        'taskObjectId': objectid,
                        'comment':      comment }
            callid = self.server.put_object( payload = payload,
                                             callback = self.callback )
            response = self.get_response(callid)
            if response:
                self.set_result(response, template=TASK_LIST_TEMPLATE)
    
    @options([make_option('--delegated', action='store_true', help='List delegated Tasks.'),
              make_option('--todo',      action='store_true', help='List To-Do Tasks [default].'),
              make_option('--archived',  action='store_true', help='List archived Tasks.'),
              make_option('--count',     action='store_true', help='Count tasks rather than list.'), ] )          
    def do_list_tasks(self, arg, opts=None):
        '''List tasks.'''
        if self.server_ok():  
            if opts.delegated: criteria = 'delegated'
            elif opts.archived: criteria = 'archived'
            else: criteria = 'todo'
            callid = self.server.search_for_objects(entity='Task',
                                                    criteria=criteria,
                                                    detail=0,
                                                    callback=self.callback)
            response = self.get_response(callid)
            if response:
                if opts.count:
                    self.set_result('{0} tasks'.format(len(response.payload)))
                else:
                    self.set_result( response, template=TASK_LIST_TEMPLATE )                                                   
                    
    @options( [ make_option('--objectid', type='int', help='ObjectId of Task to reject.'),
                make_option('--comment', type='string',help=''), ] )                             
    def do_reject_task(self, arg, opts=None):
        '''Reject the specified Task.'''
        response = self._task_action(opts.objectid, 'reject', opts.comment)
        
    @options( [ make_option('--objectid', type='int', help=''),
                make_option('--comment', type='string', help=''), ] )                             
    def do_accept_task(self, arg, opts=None):
        '''Accept the specified Task.'''    
        response = self._task_action(opts.objectid, 'accept', opts.comment)
                
    @options( [ make_option('--objectid', type='int', help=''),
                make_option('--comment', type='string', help=''), ] )                             
    def do_annotate_task(self, arg, opts=None):
        response = self._task_action(opts.objectid, 'comment', opts.comment)
                
    @options( [ make_option('--objectid', type='int', help=''),
                make_option('--comment', type='string', help=''), ] )                             
    def do_complete_task(self, arg, opts=None):
        '''Complete the specified Task.'''
        response = self._task_action(opts.objectid, 'done', opts.comment)
                
    @options( [ make_option('--objectid', type='int', help=''),
                make_option('--comment', type='string', help=''), ] )                             
    def do_reactivate_task(self, arg, opts=None):
        response = self._task_action(opts.objectid, 'reactivate', opts.comment)
                
    @options( [ make_option('--objectid', type='int', help=''), ] )                             
    def do_list_task_actions(self, arg, opts=None):
        '''List the actions/history for the specified task.'''
        response = self._get_entity(opts.objectid, detail_level=1, expected_type='Task')
        if response:
           stream = StringIO.StringIO()
           for notation in response.payload['_notes']:
               stream.write('{0} {1} {2}\n'.format(notation['action'],
                                                   notation['actorobjectid'],
                                                   notation['actiondate']))
               stream.write('{0}\n\n'.format(notation['comment']))                                                    
           self.set_result(stream.getvalue())
                
    @options( [ make_option('--objectid', type='int', 
                            help='ObjectId of Task to delete.'), ] )                             
    def do_delete_task(self, arg, opts=None):
        '''Delete the specified Task.'''
        response = self._get_entity(opts.objectid, expected_type='Task')
        if response:     
            callid = self.server.delete_object(objectid=opts.objectid,
                                               callback=self.callback)
            response = self.get_response(callid)
            if response:
                import pprint
                pprint.pprint(response.payload)
                self.set_result(response)
                
    @options( [ make_option('--objectid', type='int', help='ObjectId of Task to display.'), ] )                             
    def do_get_task(self, arg, opts=None):
        '''Retrieve task entity from the server.'''
        response = self._get_entity(opts.objectid, detail_level=16, expected_type='Task')
        if response:
            self.set_result(response, template=TASK_TEMPLATE) 

    @options( [ make_option('--childid',  type='int',  help='objectId [Task] to reparent.'),
                make_option('--parentid', type='int', help='objectId [Task] of new parent, or zero to remove parent.')])          
    def do_reparent_task(self, arg, opts=None):
        '''Change the parent task of a task, or remove the parent.'''
        response = self._get_entity( opts.childid, expected_type='Task' )
        if response:
            task = response.payload  
            if opts.parentid:
                parent = self._get_entity(opts.parentid, expected_type='Task')
                if parent:
                    parentid = parent.payload['objectid']
                else:
                    self.set_result('Specified parent is not a Task.')
                    return
            else:
                parentid = None    
            task['parenttaskobjectid'] = parentid
            callid = self.server.put_object( payload = task,
                                             callback = self.callback )
            response = self.get_response(callid)
            if response:
                self.set_result(response, template=TASK_TEMPLATE)
            else:
                self.set_result('Specified object is not a Task.')

    @options( [ make_option( '--title',     type='string', help='First name of the contact.' ),
                make_option( '--start',     default=None, type='string', help='' ),
                make_option( '--end',       default=None, type='string', help='' ),
                make_option( '--projectid', default=None, type='int', help='' ),
                make_option( '--parentid',  default=None, type='int', help='' ), ] )          
    def do_create_task(self, arg, opts=None):
        e = { 'entityName':  'Task',
              'objectId':    0,
              'start':       opts.start,
              'end':         opts.end,
              'title':       opts.title, }

        # TODO: Verify date format
        # WARN: These options do not currently work due to bugs in Cmd
        if opts.start: e[ 'start' ] = opts.start
        if opts.start: e[ 'end' ]   = opts.end

        # ProjectId
        if opts.projectid:
            parent = self._get_entity( opts.projectid, expected_type='Project' )
            if parent:
                e[ 'objectprojectid' ] = opts.projectid
            else:
                self.set_result( 'Specified project is not available.' )
                return
        
        # ParentId
        if opts.parentid:
            parent = self._get_entity( opts.parentid, expected_type='Task' )
            if parent:
                e[ 'parenttaskobjectid' ] = opts.parentid
            else:
                self.set_result( 'Specified parent is not a Task.' )
                return                
                
        callid = self.server.put_object( e, callback=self.callback )
        response = self.get_response(callid)
        if response:
            self.set_result(response, template=TASK_TEMPLATE)
        else:
            self.set_result('No response', error=True)
