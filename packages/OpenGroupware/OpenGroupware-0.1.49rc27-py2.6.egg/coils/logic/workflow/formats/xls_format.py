#
# Copyright (c) 2010, 2012, 2013
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
import StringIO
from base64      import b64encode
from lxml        import etree
from xlrd        import open_workbook
from xlwt        import Workbook, easyxf
from format      import COILS_FORMAT_DESCRIPTION_OK, COILS_FORMAT_DESCRIPTION_INCOMPLETE, Format
from exception   import RecordFormatException
from coils.foundation import Parse_Value_To_UTCDateTime, Delocalize_DateTime
from coils.foundation.api       import elementflow

class SimpleXLSFormat(Format):

    def __init__(self):
        Format.__init__(self)
        self._styles = None

    def set_description(self, fd):
        code = Format.set_description(self, fd)
        if (code[0] == 0):
            self.description = fd
            self._definition = self.description.get('data')
            for field in self.description['data']['columns']:
                if not ('kind' in field):
                    # If kind is not specified we assume type of string; this is to remain compatible
                    # with previous behavior of this format.  Perhaps a kind-string option could be
                    # added as a global format parameter to disable this permissiveness?  But it may
                    # not be work the trouble
                    field['kind'] = 'string'
                    # WARN: This code disable because incompatible with previous behavior
                    #return (COILS_FORMAT_DESCRIPTION_INCOMPLETE,\
                    #   'Incomplete Description: kind missing from <{0}> field'.format(field['name']))
            self._discard_on_error = self._definition.get('discardMalformedRecords', False)
            return (COILS_FORMAT_DESCRIPTION_OK, 'OK')
        else:
            return code

    @property
    def mimetype(self):
        return 'application/vnd.ms-excel'

    def process_in(self, rfile, wfile):
        # Identify the sheet to be opened, defaulting to sheet 0
        self._sheet_num = int( self.description.get( 'sheet', '0' ) )

        # Read the workbook
        self._book = open_workbook( file_contents=rfile.read( ) )
        # Reference the specified sheet
        self._sheet = self._book.sheet_by_index( self._sheet_num )
        # Reference the workbooks date mote
        self._datetype = self._book.datemode

        self.xml = elementflow.xml( wfile, u'ResultSet', attrs={ 'className': self.__class__.__name__,
                                                                 'formatName': self.description.get( 'name' ),
                                                                 'tableName': self.description.get( 'tableName', '_undefined_' ),
                                                               },
                                                         indent=False )
        #Get field names from first row.
        self._column_names = []
        for colx in range( self._sheet.ncols ):
            self._column_names.append( self._sheet.cell_value( rowx=0, colx=colx ) )

        with self.xml:
            for self._rowNum in range( 1, self._sheet.nrows ):
                try:
                    data = self.process_record_in( )
                    self.pause( self._rowNum )
                except RecordFormatException, e:
                    self.log.warn( 'Record format exception on row {0} column {1}: {2}'.format( self._rowNum+1, self._colNum+1, e ) )
                    if self._discard_on_error:
                        self.log.info( 'Row {0} of input message dropped due to format error'.format( self._rowNum+1 ) )
                    else:
                        raise e
        return True

    def init_styles(self):
        self._styles = { }
        source = self._definition.get('styles', [])
        for style in source:
            descriptor = 'font:{0};alignment:{1};pattern:{2}'.\
                            format(source[style].get('font', ''),
                                   source[style].get('alignment', ''),
                                   source[style].get('pattern', ''))
            format = source[style].get('format', None)
            if (format is None):
                self._styles[style] = easyxf(descriptor)
            else:
                self._styles[style] = easyxf(descriptor, num_format_str=format)

    def begin_output(self):
        if (self._styles is None):
            self.init_styles()
        self._book = Workbook(style_compression=2)
        self._sheet = self._book.add_sheet('Sheet 1')
        if ('header' in self._definition):
            self._sheet.header_str = self._definition.get('header')
        if ('footer' in self._definition):
            self._sheet.footer_str = self._definition.get('footer')
        if ('portrait' in self._definition):
            if (self._definition.get('portrait')):
                self._sheet.portrait = True
            else:
                self._sheet.portrait = False
        counter = 0
        style = self._styles.get('_title')
        for column in self._definition.get('columns'):
            if (style is None):
                self._sheet.row(0).write(counter, column.get('title'))
            else:
                self._sheet.row(0).write(counter, column.get('title'), style)
            self._sheet.col(counter).width = int(column.get('width'))
            counter = counter + 1
        self._sheet.set_panes_frozen(True)
        self._sheet.set_horz_split_pos(1)

    def end_output(self):
        pass

    def process_out(self, rfile, wfile):
        doc = etree.parse(rfile)
        self.begin_output()
        self._row = 1
        for record in doc.xpath(u'/ResultSet/row'):
            self.process_record_out(record)
            self._row = self._row + 1
        self.end_output()
        self._book.save(wfile)
        self._book = None

    def process_record_out(self, record):
        self._column = 0
        for column in self._definition.get('columns'):
            value = record.xpath(u'{0}[1]/text()'.format(column.get('name')))
            if (len(value) > 0):
                value = value[0]
            else:
                value = None
            kind  = column.get( 'kind', 'string' ) # String is the default AND fallthrough type
            style = column.get( 'style', None ) # Don't forget that dates *MUST* by styled in order to be dates
            if (style is not None):
                # A style was identified by name, get a reference to the names style from the style cache
                style = self._styles.get(style, None)

            if kind == 'float':
                if value is None: value = column.get( 'default', None )
                if value:
                    if style:
                        self._sheet.row( self._row ).write( self._column, float( value ), style )
                    else:
                        self._sheet.row( self._row ).write( self._column, float( value ) )
            elif kind == 'integer':
                if value is None: value = column.get( 'default', None )
                if value:
                    if style:
                        self._sheet.row( self._row ).write( self._column, int( value ), style )
                    else:
                        self._sheet.row( self._row ).write( self._column, int( value ) )
            elif kind in ( 'date', 'datetime' ):
                # NOTE: Excel/XLS does not actually have a datetime type.  Date values are integers
                #       which must be styled as dates!  This is an XLS issue, not a Coils issue.
                if value is None:
                    value = column.get( 'default', None )
                if value:
                    value =  Parse_Value_To_UTCDateTime( value )
                    value = Delocalize_DateTime( value )
                    if style:
                        self._sheet.row(self._row).write(self._column, value, style)
                    else:
                        self._sheet.row(self._row).write(self._column, value )
            else:
                # We fall through to treating the value as a string,  perhaps this is a bug
                # or maybe it is a feature.  It should at least capture most values into the
                # StandardXML document.
                if value:
                    value = self.decode_text( value )
                    if column.get( 'strip', 'false' ) == 'true':
                        value = value.strip( )
                if style:
                    self._sheet.row(self._row).write(self._column, value, style)
                else:
                    self._sheet.row(self._row).write(self._column, value)

            self._column = self._column + 1

        self._sheet.flush_row_data()
