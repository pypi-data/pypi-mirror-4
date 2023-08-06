#
# Copyright (c) 2012
#  Adam Tauno Williams <awilliam@whitemice.org>
#
# License: MIT/X11
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
import zipfile, shutil
from tempfile            import NamedTemporaryFile
from coils.core          import *
from coils.core.logic    import ActionCommand

class AppendToZIPFileAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "append-to-zipfile"
    __aliases__   = [ 'appendToZipFile', 'appendToZipFileAction' ]

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_mimetype(self):
        return u'application/zip'

    def do_action(self):

        #Retrieve the message witht he specifed label
        message = self._ctx.run_command( 'message::get', process=self.process,
                                                         label=self._input_label )
        if not message:
            raise CoilsException( 'Unable to marshall message labelled "{0}"'.format( self._input_label ) )
        input_handle = self._ctx.run_command( 'message::get-handle', object=message )

        # rfile is read-only, so we need to dup the contents to the wfile
        shutil.copyfileobj( self.rfile, self.wfile )
        self.wfile.seek( 0 )
        # Create the ZipFile object on the actions' write file handle
        zfile = zipfile.ZipFile( self.wfile, 'a', compression=zipfile.ZIP_DEFLATED )
        # Add the content from the message handle
        zfile.write( input_handle.name, arcname=self._filename )
        zfile.close( )

    def parse_action_parameters(self):

        self._input_label = self.action_parameters.get( 'inputLabel', '' )
        if self._input_label:
            self._input_label = self.process_label_substitutions( self._input_label )
        else:
            raise CoilsException( 'No input label specified for appendToZipFile' )

        self._filename = self.action_parameters.get( 'filename', 'noname.data' )
        self._filename = self.process_label_substitutions( self._filename )

    def do_epilogue(self):
        pass
