# Copyright (c) 2010 Adam Tauno Williams <awilliam@whitemice.org>
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
import os
from xml.sax                           import make_parser
from xml.sax.handler                   import ContentHandler
from coils.core                        import *
from coils.logic.workflow              import BPMLSAXHandler

def filename_for_route_markup(route, version):
    return 'wf/r/{0}.{1}.bpml'.format(route.name, version)

def filename_for_process_markup(process):
    return 'wf/p/{0}.bpml'.format(process.object_id)

def filename_for_process_code(process, version):
    return 'wf/p/{0}.{1}.cpm'.format(process.object_id, version)

def route_versions(route):
    versions = []
    edition = 0
    while edition < route.version:
        edition = edition + 1
        if (BLOBManager.Exists(filename_for_route_markup(route, edition))):
            versions.append(str(edition))
    return versions

def process_versions(process):
    versions = []
    edition = 0
    while edition < process.version:
        edition = edition + 1
        if (BLOBManager.Exists(filename_for_process_code(process, edition))):
            versions.append(str(edition))
    return versions

def compile_bpml(_file, log=None):
    cpm = None
    try:
        _file.seek(0)
        parser = make_parser()
        handler = BPMLSAXHandler()
        parser.setContentHandler(handler)
        parser.parse(_file)
        cpm = handler.get_processes()
        if log:
            log.debug('Successfully processed BPML document')
        if ('__namespace__' in cpm):
            description = { 'name': cpm['__namespace__'] }
            if log:
                log.debug('Determined namespace of BPML document')
        else:
            if log:
                log.warn('No namespace defined in BPML document')
            description = 'Unnamed route'
    except Exception, e:
        if log:
            log.warn('Processing of BPML document at {0} failed.'.format(_filename))
            log.exception(e)
        raise CoilsException('Processing BPML document failed.')
    else:
        return description, cpm



