#
# Copyright (c) 2010 Adam Tauno Williams <awilliam@whitemice.org>
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
from datetime           import datetime

class TaskCommand(object):

    def verify_values(self):
        # TODO: Verify parent_id is a task
        # TODO: Verify project_id is a project
        # TODO: Verify creator is an account
        # TODO: Verify owner is a contact
        # TODO: Verify priority
        # TODO: Verify sensitivity
        # TODO: Verify % complete
        # TODO: Verify start > now
        # TODO: Verify end > start
        return True

    def get_by_id(self, object_id, access_check):
        task = self._ctx.run_command('task::get', id=object_id,
                                                  access_check=access_check)
        return task

    def do_tko(self):
        pass

    def process_attachments(self):
        # We only attempt to process attachments if the incoming value is a dict - that being an
        # Omphalos representation (possibly created from a vTODO).
        if isinstance(self.values, dict):
            if '_ATTACHMENTS' in self.values:
                attachments_ = { }  # First loaded with all attachments keyed, by checksum.  Then matching
                                    # attachments [already exist] will be eliminated leaving just the
                                    # attachments that need to be created.
                deletes_     = [ ]  # Will be populated with attachment UUIDs that need to be deleted

                for attachment_ in self.values['_ATTACHMENTS']:
                    hash_ = attachment_.get('sha512checksum', None)
                    if hash_:
                        attachments_[hash_] = attachment_

                # Pivot from the enumeration of existing attachments
                for attachment in self.obj.attachments:
                    if attachment.checksum in attachments_:
                        # Attachment already exists; potentially change name?
                        name_ = attachments_[attachment.checksum]['name']
                        attachment.webdav_uid = name_ if name_ else attachment.webdav_uid
                        del attachments_[attachment.checksum] # Delete from dict, nothing more needs to be done with it
                    else:
                        # The attachment does not exist in the list of provided attachments
                        deletes_.append(attachment.uuid)

                # Loop the attachments that remain in the dict, creating new attachment entities.
                for attachment_ in attachments_.values():
                    if 'data' in attachment_:
                        # TODO: If the mimetype is 'application/octet-stream *and* we have a name, try to guess
                        #       a mimetype from the file extension
                        self._ctx.run_command('attachment::new', data = attachment_['data'],
                                                                 name = attachment_['name'],
                                                                 related_id = self.obj.object_id,
                                                                 mimetype= attachment_['mimetype'])

                # Delete the attachment entities we no longer find in the object representation
                for uuid_ in deletes_:
                    self._ctx.run_command('attachment::delete', uuid=uuid_)


