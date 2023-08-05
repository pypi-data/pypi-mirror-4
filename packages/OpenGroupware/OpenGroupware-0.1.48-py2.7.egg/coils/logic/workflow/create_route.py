#
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
#
import shutil, StringIO
from uuid                import uuid4
from coils.core          import *
from coils.core.logic    import CreateCommand
from keymap              import COILS_ROUTE_KEYMAP
from utility             import filename_for_route_markup

def default_markup(rid, name):
    action_uuid = str(uuid4())
    markup = StringIO.StringIO()
    markup.write(u'<?xml version="1.0" encoding="UTF-8"?>')
    markup.write(u'<package targetNamespace="{0}">'.format(name))
    markup.write(u'<process id="{0}" persistent="false" name="{1}">'.format(rid, name))
    markup.write(u'<event activity="{0}" exclusive="false"/>'.format(name))
    markup.write(u'<context atomic="true">')
    markup.write(u'</context>')
    markup.write(u'<action name="{0}" id="{1}" extensionAttributes="{0}/{1}">'.format(name, action_uuid))
    markup.write(u'<input property="InputMessage" formatter="StandardRaw"/>')
    markup.write(u'<output><source property="InputMessage"/></output>')
    markup.write(u'<attributes>')
    markup.write(u'<extension name="activityName">eventAction</extension>')
    markup.write(u'<extension name="isSavedInContext">true</extension>')
    markup.write(u'<extension name="description"/>')
    markup.write(u'</attributes>')
    markup.write(u'</action>')
    markup.write(u'</process>')
    markup.write(u'</package>')
    output = markup.getvalue()
    markup.close()
    return output

class CreateRoute(CreateCommand):
    __domain__ = "route"
    __operation__ = "new"

    def __init__(self):
        CreateCommand.__init__(self)

    def prepare(self, ctx, **params):
        self.keymap =  COILS_ROUTE_KEYMAP
        self.entity = Route
        CreateCommand.prepare(self, ctx, **params)

    def parse_parameters(self, **params):
        CreateCommand.parse_parameters(self, **params)
        if ('markup' in params):
            self.values['markup'] = params['markup']
        elif ('filename' in params):
            # TODO: Trap possible errors.
            handle = open(params['filename'], 'rb')
            self.values['markup'] = handle.read()
            handle.close()
        elif ('handle' in params):
            handle = params['handle']
            handle.seek(0)
            self.values['markup'] = handle.read()

    def save_route_markup(self):
        handle = BLOBManager.Create(filename_for_route_markup(self.obj), encoding='binary')
        handle.write(self.obj.get_markup())
        BLOBManager.Close(handle)

    def run(self, **params):
        CreateCommand.run(self, **params)
        if ('markup' in self.values):
            self.log.debug('New route has {0} bytes of markup.'.format(len(self.values['markup'])))
            self.obj.set_markup(self.values['markup'])
        else:
            self.log.warn('No markup specified for route')
            self.obj.set_markup(default_markup(self.obj.object_id, self.obj.name))
        self.save_route_markup()
        self.save()
