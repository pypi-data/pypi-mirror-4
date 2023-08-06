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
import time, uuid, re
from copy                import deepcopy
from email               import message_from_file
from coils.core          import *
from coils.core.logic    import ActionCommand


class MailBlastAction(ActionCommand):
    __domain__    = "action"
    __operation__ = "mail-blast"
    __aliases__   = [ 'mailBlastAction', 'mailBlastAction' ]

    def __init__(self):
        ActionCommand.__init__(self)

    def create_message_id(self):
        return '<{0}.{1}@{2}>'.format(time.time(), uuid.uuid4(), self._ctx.cluster_id)

    @property
    def assignments(self):
        return self.state[self.uuid].get('idList')

    def payload_scan(self, message, unsubscribe_id, contact):
        labels = set(re.findall('\$__[A-z0-9_]*__;', message.get_payload()))
        if (len(labels) == 0):
            return
        text = message.get_payload()
        # HACK: Opera always puts a http:// in front of links, even if the user takes it off.
        #       So if the unsubscribe labels have a protocol prefix we remove it.
        text = text.replace('http://$__UNSUBSCRIBE_LINK__;', '$__UNSUBSCRIBE_LINK__;')
        for label in labels:
            if (label == '$__UNSUBSCRIBE_LINK__;'):
                text = text.replace(label, self.unsubscribe_link.replace('{%%}', unsubscribe_id))
            elif (label == '$__UNSUBSCRIBE_TEXT__;'):
                text = text.replace(label, self.unsubscribe_text.replace('{%%}', unsubscribe_id))
            elif (label == '$__DISPLAY_NAME__;'):
                text = text.replace(label, contact.get_display_name())
            else:
                attribute = label[3:-3].lower()
                #self.log.info('mapped label "{0}" to attribute "{1}"'.format(label, attribute))
                if (hasattr(contact, attribute)):
                    text = text.replace(label, unicode(getattr(contact, attribute)))
                    #self.log.info('Using contact attribute to populate label "{0}"'.format(label))
                else:
                    #self.log.info('contact entity does not have attribute "{0}"'.format(attribute))
                    cv_text = contact.get_company_value_text(attribute)
                    if (cv_text is not None):
                        #self.log.info('Using company value to populate label "{0}"'.format(label))
                        text = text.replace(label, cv_text)
                    else:
                        pass
                        #self.log.info('label "{0}" unprocessed'.format(label))
        message.set_payload(text)

    def message_scan(self, message, unsubscribe_id, contact):
        if message.is_multipart():
            # TODO: This seem hackish; there must be a cleaner way to do this.
            # We do *not* want to walk all the attachements of the message; we only want to
            # scan : 1.) text/plain and text/html components within a multipart/alternative
            #        2.) text/plain and text/html components of a multipart/related within a
            #            multipart/alternative. (Used by Opera for HTML messages)
            #        3.) Outer text/plain and text/html components.
            # TODO: Is number #3 even necessary? Hopefully #1 covers everyone but Opera
            for part in message.get_payload():
                if (part.get_content_type() == 'multipart/alternative'):
                    for subpart in part.get_payload():
                        if ((subpart.get_content_type() == 'text/plain') or
                            (subpart.get_content_type() == 'text/html')):
                            self.payload_scan(subpart, unsubscribe_id, contact)
                        elif (subpart.get_content_type() == 'multipart/related'):
                            # Opera Hack!
                            for subsubpart in subpart.get_payload():
                                if ((subsubpart.get_content_type() == 'text/plain') or
                                    (subsubpart.get_content_type() == 'text/html')):
                                    self.payload_scan(subsubpart, unsubscribe_id, contact)
                elif ((part.get_content_type() == 'text/plain') or
                    (part.get_content_type() == 'text/html')):
                    self.payload_scan(part, unsubscribe_id, contact)
        else:
            self.payload_scan(message, unsubscribe_id, contact)

    def transform_message(self, message, contact, assignment_id, email):
        # Take the source message and make a copy, then set all the headers, etc...
        tmp_message = deepcopy(message)
        unsubscribe_id = '{0}@{1}'.format(assignment_id, self._ctx.cluster_id)
        tmp_message.replace_header('to', email)
        self.message_scan(tmp_message, unsubscribe_id, contact)
        if (tmp_message.has_key('message-id')):
            tmp_message.replace_header('message-id', self.create_message_id())
        else:
            tmp_message.add_header('Message-Id', self.create_message_id())
        if (tmp_message.has_key('X-OpenGroupware-Regarding-Workflow-Action')):
            tmp_message.replace_header('X-OpenGroupware-Regarding-Workflow-Action', str(self.uuid))
            tmp_message.replace_header('X-OpenGroupware-Regarding-Process-Id',      str(self.pid))
            tmp_message.replace_header('X-OpenGroupware-Regarding-Assignment-Id',   str(assignment_id))
            tmp_message.replace_header('X-OpenGroupware-Cluster-Id',                str(self._ctx.cluster_id))
            tmp_message.replace_header('X-OpenGroupware-Unsubscribe-Id',            str(unsubscribe_id))
        else:
            tmp_message.add_header('X-OpenGroupware-Regarding-Workflow-Action', str(self.uuid))
            tmp_message.add_header('X-OpenGroupware-Regarding-Process-Id',      str(self.pid))
            tmp_message.add_header('X-OpenGroupware-Regarding-Assignment-Id',   str(assignment_id))
            tmp_message.add_header('X-OpenGroupware-Cluster-Id',                str(self._ctx.cluster_id))
            tmp_message.add_header('X-OpenGroupware-Unsubscribe-Id',            str(unsubscribe_id))
        return tmp_message

    def load_defaults(self):
        sd = ServerDefaultsManager()
        self.suppression_attribute = sd.default_as_dict('SMTPServer').get('SuppressEMailAttribute', None)
        self.unsubscribe_link = sd.default_as_dict('SMTPServer').get('UnsubscribeLink', '')
        self.unsubscribe_text = sd.default_as_dict('SMTPServer').get('UnsubscribeText', '')
        if (self.suppression_attribute is None):
            self.log_message('No email suppression attribute configured', category='info')
        else:
            self.log_message('Email suppression attribute is "{0}"'.format(self.suppression_attribute), category='info')

    def init_state(self):
            # Initialize the state, this is the first time the action is run. One
            # assumes that this action will be invoked iteratively.
            self.state[self.uuid] = { 'sentCounter': 0, 'skipCounter': 0, 'idList': { }, 'delay': 0.1 }
            self.log_message('Current security context is id#{0}'.format(self._ctx.account_id))
            collection = self._ctx.run_command('collection::get', id=self._collection_id)
            if (collection is not None):
                assignments = self._ctx.run_command('collection::get-assignments', collection = collection,
                                                                                   entity_name = 'Contact')
                self.log_message('Found {0} contacts assigned to collectionId#{1}'.format(len(assignments), collection.object_id))
                for assignment in assignments:
                    self.assignments[assignment.assigned_id] = { 'contactId':  assignment.assigned_id,
                                                                 'processed':  False,
                                                                 'assignmentId': assignment.object_id }
            else:
                raise CoilsException('Unable to load specified collection (objectId#{0})'.format(self._collection_id))

    def load_unit_of_work(self):
        #
        # Build a unit of work
        #
        contact_ids = [ ]
        for k,v in self.assignments.iteritems():
            if (self._chunk_size < 1):
                break
            elif v['processed']:
                continue
            else:
                self._chunk_size += -1
                contact_ids.append(v['contactId'])
        if (len(contact_ids) == 0):
            self.log_message('Mail-Blast complete, assignments exhausted.', category='info')
            self.set_proceed(True)
            # END
            return [ ], [ ]
        else:
            self.log_message('Selected {0} contacts for mail-blast iteration.'.format(len(contact_ids)), category='info')
            self.set_proceed(False)
        # Process the unit of work
        contacts = self._ctx.run_command('contact::get', ids=contact_ids)
        return contact_ids, contacts

    def do_action(self):

        self.load_defaults()

        if (self.uuid not in self.state):
            self.init_state()

        # Resume counters from state
        self.sent_counter = self.state.get(self.uuid).get('sentCounter')
        self.skip_counter = self.state.get(self.uuid).get('skipCounter')

        # Parse input message
        message = message_from_file(self.rfile)

        # Load a unit of work
        contact_ids, contacts = self.load_unit_of_work()
        if ((len(contacts) == 0) and (len(contact_ids) < self._chunk_size)):
            self.log_message('Mail-Blast complete with {0} dangling assignments.'.format(len(contact_ids)), category='info')
            self.set_proceed(True)
            # END
            return
        self.log_message('Loaded {0} contacts from database'.format(len(contacts)), category='info')

        #
        # Process the unit of work
        #
        for contact in contacts:
            # Remove this object_id from the contact ids list; this way we can trim out the
            # dangling [assigned but unavailabe] contacts from the process list.
            contact_ids.remove(contact.object_id)
            # Check for email supression
            if (self.suppression_attribute is not None):
                text = contact.get_company_value_text(self.suppression_attribute)
                if (text is not None):
                    text = text.strip().lower()
                    if ((text == 'no') or (text == 'false')):
                        journal = 'E-Mail to ContactId#{0} <{1}> suppressed by attribute'.\
                                    format(contact.object_id,
                                           contact.get_display_name())
                        self.log_message(journal, category='info')
                        self.assignments[contact.object_id]['processed'] = True
                        # CONTINUE LOOP
                        continue
            # EMail was not supressed by attribute
            email = contact.get_company_value_text('email1')
            if (email is not None):
                email = email.strip()
                if (len(email) > 7):
                    tmp_message = self.transform_message(message,
                                                         contact,
                                                         self.assignments[contact.object_id]['assignmentId'],
                                                         email)
                    try:
                        SMTP.send(tmp_message.get('from'), [email], tmp_message)
                    except:
                        # Submission of e-mail to SMTP server failed
                        # This is most likely an invalid e-mail address, but could indicate a network issue
                        # TODO: What different exceptions can occur here? A bad e-mail address should just
                        #       be suppressed and the action continue.  A network related issue should cause
                        #       the action to fail [what about items aleady processed in the loop? If state is
                        #       not saved it is not possible to resume.  Should these e-mails just be queued
                        #       for send upon commit?
                        journal = 'ContactId#{0} <{1}> e-mail address "{2}" message submission failed.'.\
                                  format(contact.object_id, contact.get_display_name(), email)
                        self.skip_counter += 1
                    else:
                        # Message successfully sent
                        journal = 'Message to ContactId#{0} <{1}> sent to "{2}"'.\
                                  format(contact.object_id, contact.get_display_name(), email)
                        self.sent_counter += 1
                else:
                    # Failure due to e-mail address too short
                    journal = 'ContactId#{0} <{1}> e-mail address "{0}" considered invalid due to length'.\
                              format(contact.object_id, contact.get_display_name())
                    self.skip_counter += 1
            else:
                # Failure due to no e-mail address
                journal = 'ContactId#{0} <{1}> has no e-mail address'.\
                           format(contact.object_id, contact.get_display_name())
                self.skip_counter += 1

            self.log_message(journal, category='info')
            self.assignments[contact.object_id]['processed'] = True
            time.sleep(self.state.get(self.uuid).get('delay'))
            tmp_message = None

        for contact_id in contact_ids:
            journal = 'ContactId#{0} could not be resolved.'.format(contact.object_id)
            self.log_message(journal, category='info')
            self.skip_counter += 1
            self.assignments[contact.object_id]['processed'] = True

        self.state[self.uuid]['sentCounter'] = self.sent_counter
        self.state[self.uuid]['skipCounter'] = self.skip_counter
        journal = 'Sent message to {0} contacts, skipped {1}'.format(self.sent_counter, self.skip_counter)
        self.log_message(journal, category='info')

    def parse_action_parameters(self):
        self._chunk_size     = self.action_parameters.get('chunkSize', '150')
        self._chunk_size     = self.process_label_substitutions(self._chunk_size)
        self._chunk_size     = int(self._chunk_size)
        self._collection_id  = self.action_parameters.get('collectionId', None)
        if (self._collection_id is not None):
            self._collection_id  = self.process_label_substitutions(self._collection_id)
            try:
                tmp = int(self._collection_id)
            except Exception, e:
                raise CoilsException('CollectionId "{0}" specified is not an object id'.format(self._collection_id))
            else:
                self._collection_id = tmp
        else:
            raise CoilsException('No collection identified for e-mail blast')

    def do_epilogue(self):
        pass
