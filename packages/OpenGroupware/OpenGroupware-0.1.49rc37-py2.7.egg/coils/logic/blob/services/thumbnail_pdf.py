#
# Copyright (c) 2013
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
import shutil, signal
from coils.core           import *
from subprocess           import Popen, PIPE

CONVERSION_TIMEOUT_SECONDS=15

class TimeOutAlarm(Exception):
    pass


def timeout_alarm_handler(signum, frame):
    raise TimeOutAlarm


class ThumbnailPDF(object):

    def __init__(self, ctx, mimetype, entity, path):
        self.mimetype = mimetype
        self.context  = ctx
        self.entity   = entity
        self.pathname = path

    def create(self):

        rfile = self.context.run_command( 'document::get-handle', document=self.entity )
        if not rfile:
            return False

        converter = None
        sfile = BLOBManager.ScratchFile( )
        try:
            signal.signal(signal.SIGALRM, timeout_alarm_handler)
            signal.alarm( CONVERSION_TIMEOUT_SECONDS )

            # convert -format pdf -[0] -thumbnail 175x -bordercolor white png:-

            converter = Popen( [ '/usr/bin/convert', '-format', 'pdf', '-[0]', '-thumbnail', '175x', '-bordercolor', 'white', 'png:-', ],
                                 stdin=PIPE, stdout=sfile )
            ( converter_in, converter_out ) =  ( converter.stdin, converter.stdout )

            shutil.copyfileobj( rfile, converter_in )
            converter_in.close( )
            converter.communicate( )
            signal.alarm( 0 )
        except TimeOutAlarm:
            self.context.log.debug( 'PDF Thumbnail generation timeout for OGo#{0} [Document]'.format( self.entity.object_id ) )
            if converter:
                self.context.log.debug( 'killing converter due to timeout' )
                converter.kill( )
            return False
        except Exception as e:
            self.context.log.error( 'Unexpected exception occurred in PDF thumbnail generation for OGo#{0} [Document]'.format( self.entity.object_id ) )
            self.context.log.exception( e )
            return False
        else:
            sfile.flush( )
            sfile.seek( 0 )
            wfile = BLOBManager.Create( self.pathname.split( '/' ), 'binary' )
            shutil.copyfileobj( sfile, wfile )
            BLOBManager.Close( wfile )
            return True
        finally:
            signal.alarm( 0 )
            BLOBManager.Close( sfile )
