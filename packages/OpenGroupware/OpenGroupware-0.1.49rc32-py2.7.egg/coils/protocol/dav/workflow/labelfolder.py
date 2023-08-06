# Copyright (c) 2009 Adam Tauno Williams <awilliam@whitemice.org>
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
from coils.core                        import *
from coils.net                         import *
from messagefolder                     import MessageFolder

class LabelFolder(MessageFolder):
    def __init__(self, parent, name, **params):
        MessageFolder.__init__(self, parent, name, **params)

    @property
    def label_type(self):
        return 'label'

    def supports_PUT(self):
        return True

    def _load_contents(self):
        self.data = { }
        self.log.debug('Loading labeled messages of process {0}.'.format(self.process_id))
        messages = self.context.run_command('process::get-messages', pid=self.process_id)
        for message in messages:
            if (message.label != message.uuid):
                if (message.scope is None):
                    self.insert_child(message.label, message)
                else:
                    self.insert_child('{0}.{1}'.format(message.label, message.scope), message)
        return True

    def do_PUT(self, request_name):
        #TODO: A successful response should include an ETag
        #TODO: Does this handle updating of a Message, or only creation?
        if (self.entity.state in ['C', 'F']):
            raise AccessForbiddenException('Cannot create message in completed or failed process.')
        self.log.debug('Requested label is {0}.'.format(request_name))
        payload = self.request.get_request_payload()
        self.log.debug('Attempting to create new labeled message in process {0}'.format(self.process_id))
        try:
            message = self.create_message(process=self.entity, label=request_name, data=payload)
            self.context.commit()
            self.log.info('Message {0} created via DAV PUT by {1}.'.format(message.uuid, self.context.get_login()))
            self.context.run_command('process::start', process=self.entity)
        except Exception, e:
            self.log.exception(e)
            raise CoilsException('Failed to create labeled message')
        my_path = '/dav/Routes/{0}/{1}/Messages/{2}'.format(self.entity.route.name,
                                                            self.process_id,
                                                            message.uuid[1:-1])
        self.request.simple_response(201,
                                     mimetype='text/plain',
                                     headers= { 'Content-Length': str(message.size),
                                                'Location':       my_path } )
