#
# Copyright (c) 2011, 2013 Adam Tauno Williams <awilliam@whitemice.org>
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
from txt2pdf       import TextToPDFAction
from watermark     import WatermarkPDFAction
from lpr_print     import PrintToLPRAction
from ftpputfile    import FTPPutFileAction
from zipappend     import AppendToZIPFileAction
from todocument    import MessageToDocumentAction
from xlstoxml      import XLSToXMLAction
from folder_to_zip import FolderToZIPFileAction

try:
    import smbc
except Exception, e:

    class SMBPutFileAction(object):
        pass

    class SMBGetFileAction(object):
        pass

else:
    from smbputfile import SMBPutFileAction
    from smbgetfile import SMBGetFileAction

try:
    import zope.interface
    from z3c.rml import document, interfaces
except Exception, e:
    class RMLToPDFAction(object):
        pass
else:
    from rmltopdf import RMLToPDFAction

try:
    import cups
except Exception, e:
    class PrintToIPPAction(object):
        pass
else:
    from ipp_print import PrintToIPPAction
