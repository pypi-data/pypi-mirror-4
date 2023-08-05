#
# Copyright (c) 2010, 2012
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
import os, base64
from lxml import etree
from coils.core          import *
from coils.core.logic    import ActionCommand

#TODO: AssignAction needs love!
class AssignAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "assign"
    __aliases__   = [ 'assignAction' ]

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_mimetype(self):
        return self._output_mimetype

    def prepare_xpath_namespaces(self, namespaces):
        
        # XPath has no concept of a default namespace, so we need
        # to strip out the None-key'd namespace from the nsmap
        namespaces = dict( (prefix, namespaces[prefix]) for prefix in namespaces if prefix )        
        
        # Is this a hack?  It works really nice.
        if 'OGo' not in namespaces:
            namespaces[ 'OGo' ] = 'http://www.opengroupware.us/model'
        if 'OIE' not in namespaces:
            namespaces[ 'OIE' ] = 'http://www.opengroupware.us/oie'
        if 'OGoLegacy' not in namespaces:
            namespaces[ 'OGoLegacy' ] = 'http://www.opengroupware.org/'
        if 'OGoDAV' not in namespaces:            
            namespaces[ 'OGoDAV' ] = '57c7fc84-3cea-417d-af54-b659eb87a046'     
        if 'OGoCloud' not in namespaces:            
            namespaces[ 'OGoCloud' ] = '2f85ddbe-28f5-4de3-8de9-c96bdd5230dd'   
             
        return namespaces
            
    def do_action(self):
        if self._xpath is None:
            self.wfile.write( self._default )
        else:
            value = self._default
            doc = etree.parse( self.rfile )
            self.log.debug( etree.tostring(doc) )
            
            # Get the namespaces
            namespaces = self.prepare_xpath_namespaces( doc.getroot( ).nsmap )
            
            # Perform the lookup
            try:
                result = doc.xpath( self._xpath, namespaces=namespaces )
            except TypeError, e:
                self.log.error( 'TypeError with namespaces of: {0}'.format( namespaces ) )
                raise e
            
            # Process the lookup Results
            if isinstance( result, list ):
                if len( result ):
                    if result[0] is not None:
                        # TODO: What if this result isn't text?
                        value = str( result[ 0 ] )
                        
            # Write the result to the output message buffer
            self.wfile.write( value )

    def parse_action_parameters(self):
        self._xpath           = self.action_parameters.get('xpath', None)
        self._default         = self.action_parameters.get('default', '')
        self._output_mimetype = self.action_parameters.get('mimetype', 'application/xml')
        
        if self._xpath is not None:
            self._xpath = self.decode_text( self._xpath )
            # This check is in case the decode reduced to an emtpy string (Possible?)
            if self._xpath:
                self._xpath = self.process_label_substitutions(self._xpath)
            else:
                self._xpath = None
                
        if self._default:
            self._default = self.process_label_substitutions(self._default)

    def do_epilogue(self):
        pass
