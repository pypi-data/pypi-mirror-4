#
# Copyright (c) 2011, 2012
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
from coils.core           import CoilsException
from coils.core.logic     import ActionCommand
from coils.foundation.api.pypdf import  PdfFileWriter, PdfFileReader

class WatermarkPDFAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "watermark-pdf"
    __aliases__   = [ 'watermarkPDF', 'watermarkPDFAction' ]

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_mimetype(self):
        return 'application/pdf'

    def get_document_from_path(self, number, path):
        project = self._ctx.run_command( 'project::get', number=number )
        if not project:
            raise CoilsException( 'Unable to marshall project "{0}" specified in path to watermark.'.format( number ) )
        document = self._ctx.run_command( 'project::get-path', path=path, project=project )
        if not document:
            raise CoilsException( 'Unable to marshall watermark document from path "{0}" in projectId#{1}'.format( path, project.object_id ) )
        return document

    def do_action(self):
        #
        # Setup
        #
        if (self.input_message.mimetype != 'application/pdf'):
            raise CoilsException('Input message for PDF watermarking is not PDF')
        if (self._document_id is None):
           # Document was not specified by id, so we are looking it up by the specified path
           watermark_d = self.get_document_from_path(self._project_number, self._project_path)
        else:
            # NOTE: There isn't any technical reason we can't skip this step and jump straight to retrieving the
            #       handle to the document's contents using the id - but doing this in two steps makes the error
            #       reporting clearer if something goes wrong, or more likely, either the security context of
            #       this process does not have read-access to the document which is intended to serve as the
            #       watermark document or that document has been absent mindedly deleted [gotta love those users!]
            watermark_d = self._ctx.run_command('document::get', id=self._document_id)
            if (watermark_d is None):
                # Unable to retrieve the specified document
                raise CoilsException('Unable to retrieve documentId#{0}'.format(self._document_id))
        # TODO: Verify that the mimetype of the watermark document is 'application/pdf'
        # Get handle to document contents
        watermark_h = self._ctx.run_command('document::get-handle', document=watermark_d)
        if (watermark_h is None):
            # Not able get a handle to the documents content [filesystem issues?]
            raise CoilsException('Unable to retrieve handle for contents of documentId#{0}'.format(self._document_id))
        #
        # PDF Processing
        #
        # Open a PDF reader on the handle to the watermark document
        watermark_r = PdfFileReader(watermark_h)
        # Open a PDF reader on the handle of the action's input message (the document to be watermarked)
        input_r = PdfFileReader(self._rfile)
        # Create a PDF writer
        output_w = PdfFileWriter()
        # Loop through all the pages of the input document, doing the watermark, generating the output document
        for i in range(0, input_r.numPages):
            page_in = input_r.getPage(i)
            # Get the dimensions of the input page; do not assume all pages are the same size
            rect = page_in.mediaBox
            # Create a new page in the output document of the same dimensions
            page_out = output_w.addBlankPage(width=rect.getWidth(), height=rect.getHeight())
            # Merge the watermark onto the new page
            # TODO: Can we crop/scale the watermark to match the size of the output page if they differ?
            page_out.mergePage(watermark_r.getPage(0))
            # Merge the page from the source document onto the new page
            #   - Order matters:  this gets merged on-top, so on-top-of the watermark.
            page_out.mergePage(page_in)
        # Write the watermarked document to the action's output buffer
        output_w.write(self._wfile)

    def parse_action_parameters(self):
        # Watermark document is the only parameter; we accept either a documentId (which is an objectId of
        # a document entity) or a path which is "projectNumber:path-to-document".  We defer to the documentId
        # if both are specified.
        document_id  = self.action_parameters.get('documentId', None)
        if (document_id is None):
            path_to_watermark  = self.action_parameters.get('path', None)
            if (path_to_watermark is None):
                raise CoilsException('No watermark document specified')
            tmp = path_to_watermark.split(':')
            if (len(tmp) != 2):
                raise CoilsException('Path to watermark document cannot be parsed.')
            else:
                self._document_id  = None
                self._project_number = tmp[0]
                self._project_path   = tmp[1]
        else:
            try:
                document_id = self.process_label_substitutions(document_id)
                self._document_id = int(document_id)
            except:
                raise CoilsException('Watermark documentId of "{0}" is not a valid objectId'.format(document_id))

    def do_epilogue(self):
        pass
