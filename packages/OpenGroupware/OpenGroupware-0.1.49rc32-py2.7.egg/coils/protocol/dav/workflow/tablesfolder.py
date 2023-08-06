# Copyright (c) 2011, 2012
#  Adam Tauno Williams <awilliam@whitemice.org>
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
import json
from coils.core                        import *
from coils.logic.workflow              import Table
from coils.net                         import DAVFolder, StaticObject
from tableobject                       import TableObject


class TablesFolder(DAVFolder):
    def __init__(self, parent, name, **params):
        DAVFolder.__init__(self, parent, name, **params)

    def supports_PUT(self):
        return True

    def supports_DELETE(self):
        return True

    def _load_contents(self):
        if (self.name == 'Tables'):
            for name in Table.List():
                try:
                    table = Table.Load(name)
                except Exception, e:
                    # TODO: Raise an administrative notice. (see Issue#149)
                    pass
                else:
                    self.insert_child('{0}.yaml'.format(name), table)
        else:
            return False
        return True

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):
        if (self.load_contents()):
            if (self.has_child(name)):
                return TableObject(self,
                                    name,
                                    entity=self.get_child(name),
                                    context=self.context,
                                    request=self.request)
        self.no_such_path()

    def do_PUT(self, request_name):
        ''' Allows tables to be created by dropping YAML documents into /dav/Workflow/Tables '''
        try:
            payload = self.request.get_request_payload()
            table = self.context.run_command('table::new', yaml=payload)
        except Exception, e:
            self.log.exception(e)
            raise CoilsException('Table creation failed.')
        self.context.commit()
        if ((self.context.user_agent_description['webdav']['supports301']) and
            (table.name != request_name[:-5])):
            self.request.simple_response(301,
                                         headers= {
                                            'Location': u'/dav/Workflow/Tables/{0}.yaml'.format(table.name)
                                         } )
        else:
            self.request.simple_response(201)

    def do_DELETE(self, name):

        if name.endswith( '.yaml' ):
            name = name[ :-5 ]
        
        if Table.Delete( name ):
            self.request.simple_response(204)
        else:
            self.no_such_path( )
