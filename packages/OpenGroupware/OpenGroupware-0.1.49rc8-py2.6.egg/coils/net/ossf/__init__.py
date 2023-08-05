#
# Copyright (c) 2010, 2011 Adam Tauno Williams <awilliam@whitemice.org>
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
from coils.core    import CoilsException, NotImplementedException
from json_         import JSONOSSFilter
from xpath         import XPathOSSFilter
from thumbnail     import ImageThumbnailOSSFilter
from convert       import ImageConvertOSSFilter
from pdftotxt      import PDFToTextOSSFilter

def MarshallOSSFChain(rfile, mimetype, parameters, log=None, ctx=None):
    if ('ossfchain' in parameters):
        if isinstance(parameters['ossfchain'], list):
            if len(parameters['ossfchain']) > 0:
                ossfchain = parameters['ossfchain'][0]
            else:
                # ossfchain has no values (Possible?)
                return rfile
        elif isinstance(parameters['ossfchain'], basestring):
            ossfchain = parameters['ossfchain']
        else:
            raise CoilsException('Unable to parse ossfchain parameter')
        ossfchain = ossfchain.split(',')
        chainparams = { }
        for i in range(0, len(ossfchain)):
            chainparams[i] = { }
            for name in parameters:
                prefix = '{0}.'.format(i)
                if name[0:len(prefix)] == prefix:
                    key = name[len(prefix):]
                    if isinstance(parameters[name], list):
                        chainparams[i][key] = parameters[name][0]
                    else:
                        chainparams[i][key] = parameters[name]
        for i in range(0, len(ossfchain)):
            # TODO: Make OSSF discover modular and dynamic, this is a HACK
            if ossfchain[i] == 'json':
                ossf = JSONOSSFilter(rfile, mimetype, chainparams[i], log=log, ctx=ctx)
            elif ossfchain[i] == 'xpath':
                ossf = XPathOSSFilter(rfile, mimetype, chainparams[i], log=log, ctx=ctx)
            elif ossfchain[i] == 'thumbnail':
                ossf = ImageThumbnailOSSFilter(rfile, mimetype, chainparams[i], log=log, ctx=ctx)
            elif ossfchain[i] == 'convert':
                ossf = ImageConvertOSSFilter(rfile, mimetype, chainparams[i], log=log, ctx=ctx)
            elif ossfchain[i] == 'pdftotext':
                ossf = PDFToTextOSSFilter(rfile, mimetype, chainparams[i], log=log, ctx=ctx)
            else:
                raise CoilsException('No such OSSF as {0}'.format(ossfchain[i]))
            mimetype = ossf.mimetype
            rfile    = ossf.handle
        return rfile, mimetype
    else:
        return rfile, mimetype