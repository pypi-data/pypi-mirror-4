#
# Copyright (c) 2013 Adam Tauno Williams <awilliam@whitemice.org>
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
from xml.sax.saxutils import escape as xmlescape
from xlrd          import xldate_as_tuple, empty_cell, open_workbook
from xlrd          import XL_CELL_EMPTY, XL_CELL_NUMBER, XL_CELL_TEXT, XL_CELL_DATE
from coils.foundation.api.elementflow import elementflow
from coils.foundation import StandardXML
from coils.core.logic import ActionCommand

class XLSToXMLAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "xls-to-xml"
    __aliases__   = [ 'xlsToXmlAction', 'xlsToXml' ]

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_mimetype(self):
        return 'application/xml'

    def open_workbook(self, rfile):
        book = open_workbook( file_contents=rfile.read( ) )
        sheet = book.sheet_by_index( 0 )
        return sheet, book.datemode

    def index_from_first_row(self, sheet):
        # Build index based on first row
        index = { }
        for colx in range( sheet.ncols ):
            label = sheet.cell_value( rowx=0, colx=colx )
            if isinstance( label, basestring ):
                label = label.strip( )
                if label:
                    native_label = label
                    xml_label = label.replace( ' ', '_' ).replace( '/', '_').replace('\\', '_').replace( '-', '_')
                    xml_label = xml_label.lower( )
                    index[ colx ] = ( native_label, xml_label )
        return index

    def read_sheet_to_xml(self, sheet, wfile, index, datemode):
        # Generate output, reading all rows after first row based on first row headings
        namespaces = { }
        with elementflow.xml( wfile, u'ResultSet', namespaces=namespaces ) as xml:
            for rowx in range( 1, sheet.nrows ):
                with xml.container( 'row', attrs={ } ) as xml:
                    for colx, labels in index.items( ):
                        cell = sheet.cell( rowx=rowx, colx=colx )
                        date_type = 'undefined'
                        is_null = False
                        if cell.ctype == XL_CELL_NUMBER:
                            data_type = 'float'
                            value = float( cell.value )
                        elif cell.ctype == XL_CELL_TEXT:
                            data_type = 'string'
                            value = unicode( cell.value )
                            if not value:
                                is_null = Truemv
                        elif cell.ctype == XL_CELL_DATE:
                            data_type = 'datetime'
                            value = unicode( xldate_as_tuple( cell.value, datemode )[ 0:3 ] )
                            value = StandardXML.Reformat_Date_String( value, '(%Y, %m, %d)', '%Y-%m-%d %H:%M:%S' )
                        else:
                            is_null = True
                            # TODO: or raise-error

                        if is_null:
                            xml.element( labels[ 1 ], attrs={ 'label': xmlescape( labels[ 0 ] ), 'isNull': 'true', 'dataType': 'undefined', } )
                        else:
                            xml.element( labels[ 1 ], attrs={ 'label': xmlescape( labels[ 0 ] ), 'isNull': 'false', 'dataType': data_type,  },
                                                      text=unicode( value ) )

    def do_action(self):
        sheet, datemode = self.open_workbook( rfile=self.rfile )
        index = self.index_from_first_row( sheet=sheet )
        self.read_sheet_to_xml( sheet=sheet, wfile=self.wfile, index=index, datemode=datemode, )

    def do_test(self, rfile, wfile):
        self._rfile = rfile
        self._wfile = wfile
        self.do_action( )

