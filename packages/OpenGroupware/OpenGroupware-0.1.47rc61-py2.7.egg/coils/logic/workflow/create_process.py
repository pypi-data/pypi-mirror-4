#
# Copyright (c) 2009, 2011, 2012
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
#
import pickle, shutil, traceback
from xml.sax              import make_parser
from bpml_handler         import BPMLSAXHandler
from coils.core           import *
from coils.core.logic     import CreateCommand
from keymap               import COILS_PROCESS_KEYMAP
from utility              import filename_for_process_markup, \
                                   filename_for_process_code, \
                                   filename_for_route_markup, \
                                   parse_property_encoded_acl_list

class CreateProcess(CreateCommand):
    __domain__ = "process"
    __operation__ = "new"

    def __init__(self):
        CreateCommand.__init__(self)

    def prepare(self, ctx, **params):
        self.keymap =  COILS_PROCESS_KEYMAP
        self.entity = Process
        CreateCommand.prepare(self, ctx, **params)

    def parse_parameters(self, **params):
        CreateCommand.parse_parameters(self, **params)
        self.do_rewind = params.get('rewind', True)
        if ('data' in params):
            self.values['data'] = params['data']
        elif ('filename' in params):
            self.values['handle'] = os.open(params['filename'], 'rb')
        elif ('handle' in params):
            self.values['handle'] = params['handle']
        self._mimetype = params.get('mimetype', 'application/octet-stream')

    def copy_markup(self, route):
        # TODO: Error meaningfully if the route has no markup
        source = BLOBManager.Open(filename_for_route_markup(route), 'rb')
        target = BLOBManager.Create(filename_for_process_markup(self.obj))
        shutil.copyfileobj(source, target)
        target.flush()
        source.seek(0)
        bpml = source.read()
        BLOBManager.Close(source)
        BLOBManager.Close(target)
        self.obj.set_markup(bpml)

    def compile_markup(self):
        # TODO: Use the markup already in memory!
        handle = BLOBManager.Open(filename_for_process_markup(self.obj), 'rb', encoding='binary')
        parser = make_parser()
        handler = BPMLSAXHandler()
        parser.setContentHandler(handler)
        parser.parse(handle)
        code = handler.get_processes()
        BLOBManager.Close(handle)
        handle = BLOBManager.Create(filename_for_process_code(self.obj), encoding='binary')
        pickle.dump(code, handle)
        BLOBManager.Close(handle)


    def copy_default_acls_from_route(self, process, route):
        default_acls = self._ctx.property_manager.get_property( route,
                                                                'http://www.opengroupware.us/oie',
                                                                'defaultProcessACLs' )
        if default_acls:
            try:
                acls = parse_property_encoded_acl_list(default_acls.get_value())
                if acls:
                    for acl in acls:
                        self._ctx.run_command('object::set-acl', object      = process,
                                                                 context_id  = int(acl[0]),
                                                                 action      = acl[1],
                                                                 permissions = acl[2])
                        self.log.debug( 'Applied default ACL for contextId#{0}'.format( int(acl[0]) ) )
            except CoilsException, e:
                message = traceback.format_exc()
                self.log.exception(e)
                if (self._ctx.amq_available):
                    self._ctx.send_administrative_notice(
                        category='workflow',
                        urgency=7,
                        subject='Unable to apply defaultProcessACLs value to processId#{0}'.format(process.object_id),
                        message=message)
                return False
            else:
                return True
        else:
            return True

    def run(self, **params):
        # TODO: Verify MIME f input message against MIME of input message for route.
        CreateCommand.run(self, **params)
        # Verify route id
        route = None
        if self.obj.route_id:
            route = self._ctx.run_command('route::get', id=self.obj.route_id,
                                                        access_check=self.access_check)
        if route:
            # Route is available

            # Allocate the input message of the process
            message = None
            if ('data' in self.values):
                message = self._ctx.run_command('message::new', process=self.obj,
                                                                mimetype=self._mimetype,
                                                                label=u'InputMessage',
                                                                data=self.values['data'])
            elif ('handle' in self.values):
                message = self._ctx.run_command('message::new', process=self.obj,
                                                                mimetype=self._mimetype,
                                                                label=u'InputMessage',
                                                                rewind=self.do_rewind,
                                                                handle=self.values['handle'])
            else:
                raise CoilsException('Cannot create process without input')
            self.obj.input_message = message.uuid
            self.copy_markup(route)
            self.compile_markup()
            self.save()
            shelf = BLOBManager.OpenShelf(uuid=self.obj.uuid)
            shelf.close()

            # Feature added for 0.1.45
            # Default ACLs copied from object property of the route
            self.copy_default_acls_from_route( self.obj, route )
                     
        else:
            # TODO Support ad-hoc processes
            raise CoilsException('No such route or route not available')
