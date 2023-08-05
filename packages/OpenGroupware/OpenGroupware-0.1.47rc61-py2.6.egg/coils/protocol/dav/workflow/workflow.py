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
# THE SOFTWARE.
#

class WorkflowPresentation(object):

    def create_message(self, process=None, data=None, label=None):
        return self.context.run_command('message::new', process=process,
                                                         label=label,
                                                         data=data)

    def create_process(self, route=None, data=None, priority=200, mimetype=None):
        if (mimetype is None):
            mimetype = 'application/octet-stream'
        return self.context.run_command('process::new', values={ 'route_id': route.object_id,
                                                                  'data':     data ,
                                                                  'priority': priority },
                                                        mimetype=mimetype )

    def get_input_message(self, process):
        return self.context.run_command('process::get-input-message', process=process)

    def start_process(self, process):
        self.context.run_command('process::start', process=process)

    def get_process_messages(self, process):
        return self.context.run_command('process::get-messages', pid=process.object_id)

    def get_process_urls(self, process):
        return {'self':   '{0}/{1}/input'.format(self.get_path(), process.object_id),
                 'output': '{0}/{1}/output'.format(self.get_path(), process.object_id) }

    def get_message_handle(self, message):
        return self.context.run_command('message::get-handle', uuid=message.uuid)

    def signal_queue_manager(self):
        self.context.send('coils.http.worker/__null:',
                          'coils.workflow.queueManager/checkQueue:0',
                          None)
