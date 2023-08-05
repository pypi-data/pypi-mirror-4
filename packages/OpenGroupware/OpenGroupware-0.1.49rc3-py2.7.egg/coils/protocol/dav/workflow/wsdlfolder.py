#
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
# THE SOFTWARE.
#
import json
from coils.core                        import *
from coils.net                         import DAVFolder, StaticObject
from wsdlobject                        import WSDLObject
from coils.logic.workflow              import WSDLDocument


class WSDLFolder(DAVFolder):
    def __init__(self, parent, name, **params):
        DAVFolder.__init__(self, parent, name, **params)

    def supports_PUT(self):
        return True

    def _load_contents(self):
        for name in WSDLDocument.List():
			print name
			try:
				xsd = WSDLDocument.Marshall(name)
			except Exception, e:
				# TODO: Raise an administrative notice. (see Issue#149)
				pass
			else:
				self.insert_child(name, WSDLObject(self, name, entity=xsd, context=self.context, request=self.request))
        return True

    #def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):
    #    self.no_such_path()

    def do_PUT(self, request_name):
        ''' Allows tables to be created by dropping YAML documents into /dav/Workflow/Tables '''
        try:
            payload = self.request.get_request_payload()
            # TODO: Verify that payload is XSD data
            wsdl = WSDLDocument.Marshall(request_name)
            wsdl.fill(data=payload)
            wsdl.close()
        except Exception, e:
            self.log.exception(e)
            raise CoilsException('XSD Object Creation Failed.')
        self.context.commit()
        self.request.simple_response(201)
        
    def do_DELETE(self, request_name):
        if self.load_contents():
            if self.has_child(request_name):
                xsd = self.get_child(request_name)
                xsd.entity.delete()
                self.request.simple_response(204,
                             data=None,
                             mimetype='application/xml',
                             headers={ } )
                return
            else:
                self.no_such_path()
        else:
            raise CoilsException('Unable to enumerate collection contents.')        
