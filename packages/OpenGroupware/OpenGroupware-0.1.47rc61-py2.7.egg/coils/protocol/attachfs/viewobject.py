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
# THE SOFTWARE.
#
from coils.core           import *
from coils.net            import PathObject
from documentobject       import DocumentObject
from attachmentobject     import AttachmentObject
from messageobject        import MessageObject
from processobject        import ProcessObject

class ViewObject(PathObject):

    def __init__(self, parent, name, **params):
        self.name = name
        PathObject.__init__(self, parent, **params)

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):
        if (self.name == 'download'):
            disposition = 'attachment'
        else:
            disposition = 'inline'
        if (name.isdigit()):
            kind = self.context.type_manager.get_type(int(name))
        else:
            kind = 'attachment'
        if (kind == 'attachment'):
            entity = self.context.run_command('attachment::get', uuid=name)
            if entity:
                return AttachmentObject(self, name, entity=entity,
                                                    disposition=disposition,
                                                    parameters=self.parameters,
                                                    request=self.request,
                                                    context=self.context)
            if name.startswith('{'):
                message_uuid = name
            else:
                message_uuid = '{{{0}}}'.format(name)
            entity = self.context.run_command('message::get', uuid=message_uuid)
            if entity:
                return MessageObject(self, name, entity=entity,
                                                 disposition=disposition,
                                                 parameters=self.parameters,
                                                 request=self.request,
                                                 context=self.context)
            raise CoilsException('Unable to access attachment "{0}"'.format(name))
        elif (kind == 'Document'):
            entity = self.context.run_command('document::get', id=int(name))
            if (entity is None):
                raise CoilsException('Unable to access documentId#{0}'.format(name))
            return DocumentObject(self, name, entity=entity,
                                              disposition=disposition,
                                              parameters=self.parameters,
                                              request=self.request,
                                              context=self.context)
        elif (kind == 'Process'):
            entity = self.context.run_command('process::get', id=int(name))
            if (entity is None):
                raise CoilsException('Unable to access processId#{0}'.format(name))
            return ProcessObject(self, name, entity=entity,
                                             disposition=disposition,
                                             parameters=self.parameters,
                                             request=self.request,
                                             context=self.context)

        else:
            raise CoilsException('Unable to access object type "{0}" via attachfs.'.format(kind))
