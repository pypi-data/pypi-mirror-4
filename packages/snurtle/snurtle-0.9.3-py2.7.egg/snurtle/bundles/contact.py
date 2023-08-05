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

LIST_CONTACT_TEMPLATE = '''<%
  flags = ''
  if report['isaccount']: flags += 'a'
  if report['isprivate']: flags += 'p'
  flags = '{:^6}'.format( flags )
  
  if report['fileas']:
    name = report['fileas']
  elif report['displayname']:
    name = report['displayname']
  else: name = '{0}, {1}'.format(report['lastname'], report['firstname'])
  name = '{:<35}'.format(name)
  
  objectid = '{:<12}'.format(report['objectid'])
  
%>${objectid} ${name} ${flags}'''

CONTACT_TEMPLATE = '''    OGo#${report['objectid']} login: "${report['login']}"  version: ${report['version']} sensitivity: ${report['sensitivity']}
    isPrivate: ${report['isprivate']} isAccount: ${report['isaccount']} ownerId: ${report['ownerobjectid']}
    =================================================================
    firstName:      "${report['firstname']}" 
    lastName:       "${report['lastname']}" 
    displayName:    "${report['displayname']}"
    birthName:      "${report['birthname']}"
    birthPlace:     "${report['birthplace']}"
    citizenship:    "${report['citizenship']}"
    familyStatus:   "${report['familystatus']}"
    fileAs:         "${report['fileas']}"
    gender:         "${report['gender']}" 
    salutation:     "${report['salutation']}"
    assistantsName: "${report['assistantname']}"
    managersName:   "${report['managersname']}"
    keywords:       "${report['keywords']}"
    asoc.Categories:"${report['associatedcategories']}"
    asoc.Companies: "${report['associatedcompany']}"
    asoc.Contacts:  "${report['associatedcontacts']}"
    birthDate:      "${report['birthdate']}" 
    deathDate:      "${report['deathdate']}"
    degree:         "${report['degree']}"
    department:     "${report['department']}"
    occupation:     "${report['occupation']}"
    office:         "${report['office']}"
    url:            <${report['url']}>
    %for cv in report['_companyvalues']:
    ${'{0}:'.format(cv['attribute']).ljust(16)} "${str(cv['value']).strip()}" [type: "${cv['type']}" uid: "${cv['uid']}"]
    %endfor
    %for address in report['_addresses']:
    --address [objectId#${address['objectid']} type:${address['type']}]--
    name1:      ${address['name1']}
    name2:      ${address['name2']}
    name3:      ${address['name3']}
    street:     ${address['street']}
    locality:   ${address['city']}
    district:   ${address['district']}
    province:   ${address['state']}
    country:    ${address['country']}
    postalCode: ${address['zip']}
    %endfor
    %for phone in report['_phones']:
    --telephone [objectId#${phone['objectid']} type:${phone['type']}]--
    number:     ${phone['number']}
    info:       ${phone['info']}
    %endfor
    --enterprises--
    %if len(report['_enterprises']) == 0:
      Contact is assigned to no enterprises.
    %else:
      %for assignment in report['_enterprises']:
      ${assignment['targetobjectid']}
      %endfor
    %endif
    --projects--
    %if len(report['_projects']) == 0:
      Contact is assigned to no projects.
    %else:
      %for assignment in report['_projects']:
      ${assignment['targetobjectid']}
      %endfor
    %endif    

  '''

class ContactCLIBundle(CLIBundle):

    @options([make_option('--favorite', action='store_true',  help='List favorite contacts.')])
    def do_list_contacts(self, arg, opts=None):
        if opts.favorite:
            callid = self.server.get_favorites(entity_name='Contact', detail_level=0, 
                                                                      callback=self.callback,
                                                                      feedback=self.pfeedback)
            response = self.get_response(callid)
        if response:
            self.set_result(response, template=LIST_CONTACT_TEMPLATE)

    @options([make_option('--objectid', type='int', help='objectId [Contact] to display.'),])
    def do_get_contact(self, arg, opts=None):
        response = self._get_entity(opts.objectid, expected_type='Contact', detail_level=65535)
        if response:
            self.set_result(response, template=CONTACT_TEMPLATE)
            
    @options([])
    def do_list_accounts(self, arg, opts=None):
        callid = self.server.search_for_objects(entity='Contact', criteria=[{'key':'isAccount', 'value': 1}], detail=0, callback=self.callback)
        response = self.get_response(callid)
        if response:
            self.set_result(response.payload, template=LIST_CONTACT_TEMPLATE)
            
    @options( [ make_option( '--firstname',    dest='firstname', type='string', help='First name of the contact.' ),
                make_option( '--lastname',     dest='lastname', type='string', help='' ),
                make_option( '--displayname',  dest='displayname', type='string', default='x', help='' ),
                make_option( '--fileas',       dest='fileas', type='string', default='x', help='Attribute name' ),
                make_option( '--middlename',   dest='middlename', type='string', default='x', help='ObjectProperty value' ),
                make_option( '--private',      dest='private', action='store_true', help='ObjectProperty value' ) ] )          
    def do_create_contact(self, arg, opts=None):
        '''Set, or create, the specified object property.'''
        e = { 'entityName':  'Contact',
              'objectId':    0,
              'firstName':   opts.firstname,
              'lastName':    opts.lastname,
              'displayName': opts.displayname,
              'fileAs':      opts.fileas,
              'middleName':  opts.middlename }
        if opts.private: e[ 'isPrivate' ] = 1
        callid = self.server.put_object( e, callback=self.callback )
        response = self.get_response(callid)
        if response:
            self.set_result(response, template=CONTACT_TEMPLATE)
        else:
            self.set_result('No response', error=True)

            
