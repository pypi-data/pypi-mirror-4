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

ENTERPRISE_TEMPLATE = '''
  objectId#${report['objectid']} version: ${report['version']} sensitivity: ${report['sensitivity']}
    isPrivate: ${report['isprivate']} isCustomer: ${report['iscustomer']} ownerId: ${report['ownerobjectid']}
    =================================================================
    name:           "${report['name']}" 
    bank:           "${report['bank']}" 
    email:          "${report['bankcode']}"
    url:            "${report['url']}"
    fileAs:         "${report['fileas']}"
    keywords:       "${report['keywords']}"
    asoc.Categories:"${report['associatedcategories']}"
    asoc.Companies: "${report['associatedcompany']}"
    asoc.Contacts:  "${report['associatedcontacts']}"
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
    --contacts--
    %if len(report['_contacts']) == 0:
      No contacts are assigned to the enterprise.
    %else:
      %for assignment in report['_contacts']:
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

class EnterpriseCLIBundle(CLIBundle):

    @options([make_option('--favorite', action='store_true',  help='List favorite enterprises.')])
    def do_list_enterprises(self, arg, opts=None):
        if opts.favorite:
            callid = self.server.get_favorites(entity_name='Enterprise', 
                                               detail_level=0, 
                                               callback=self.callback,
                                               feedback=self.pfeedback)
        response = self.get_response(callid)
        if response:
            self.set_result(response)

    @options([make_option('--objectid', type='int', help='objectId [Enterprise] to display.'),])
    def do_get_enterprise(self, arg, opts=None):
        response = self._get_entity(opts.objectid, expected_type='Enterprise', detail_level=65535)
        if response:
            self.set_result(response, template=ENTERPRISE_TEMPLATE)
