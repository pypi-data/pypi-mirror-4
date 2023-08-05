#
# Copyright (c) 2011 Adam Tauno Williams <awilliam@whitemice.org>
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
from coils.core.logic    import ActionCommand
from coils.core          import *

class UnsubscribeAction(ActionCommand):
    __domain__    = "action"
    __operation__ = "mail-unsubscribe"
    __aliases__   = [ 'unsubscribeMailAction', 'unsubscribeMail' ]

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def assignments(self):
        return self.state[self.uuid].get('idList')

    def load_defaults(self):
        sd = ServerDefaultsManager()
        self.suppression_attribute = sd.default_as_dict('SMTPServer').get('SuppressEMailAttribute', None)
        if (self.suppression_attribute is None):
            self.log_message('No email suppression attribute configured', category='info')
        else:
            self.log_message('Email suppression attribute is "{0}"'.format(self.suppression_attribute), category='info')

    def read_assignment_ids(self):
        assignments = [ ]
        for entry in self._rfile.xreadlines():
            components =  [x.strip() for x in entry.split('@')]
            if (len(components) == 2):
                if (components[1] == self._ctx.cluster_id):
                    if (components[0].isdigit()):
                        assignments.append(int(components[0]))
        return assignments

    def do_action(self):
        self.load_defaults()
        if (self.suppression_attribute is None):
            self.log_message('No e-mail supression attribute configured.', category='warn')
            return
        assignments = self.read_assignment_ids()
        self.log_message('Processing {0} unsubscribe requests.'.format(len(assignments)), category='info')
        assignments = self._ctx.run_command('collection::get-assignment', ids=assignments)
        counter = 0
        for k,v in assignments.iteritems():
            counter += 1
            if (isinstance(v[1], Contact)):
                contact = v[1]
                text = contact.get_company_value_text(self.suppression_attribute)
                if (text is None) or (text.strip().lower() not in ('no', 'false')):
                    self._ctx.run_command('contact::set', object=contact,
                                                          values={'_COMPANYVALUES': [ { 'attribute': self.suppression_attribute,
                                                                                        'value': 'no' } ] } )
                    self.log_message('ContactId#{0} <{1}> bulk-email disabled by request'.\
                                     format(contact.object_id, contact.get_display_name()), category='info')
                    # TODO: Add a note to the contact indicating when & why bulk e-mail was disabled
                else:
                    self.log_message('ContactId#{0} <{1}> bulk-email already disabled.'.\
                                     format(contact.object_id, contact.get_display_name()), category='info')
            else:
                self.log_message('objectId#{0} is not a Contact entity [{1}]'.format(k, v[1]), category='info')
        if (counter == 0):
            self.log_message('No assignments from input could be resolved', category='info')
        else:
            self.log_message('{0} assignments from input processed.'.format(counter), category='info')

    def parse_action_parameters(self):
        pass

    def do_epilogue(self):
        pass
