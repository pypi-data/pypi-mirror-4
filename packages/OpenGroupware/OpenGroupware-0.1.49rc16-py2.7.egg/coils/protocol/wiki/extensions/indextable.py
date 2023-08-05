#
# Copyright (c) 2012 Tauno Williams <awilliam@whitemice.org>
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
from argparse import ArgumentParser
from shlex import split as _split
import markdown
from markdown.util import etree
from coils.core import Folder, Document

# shlex's split is broken in regards to Unicode in late Python 2.5 and
# most of Python 2.6.x.  It will turn everyting into UCS-4 regardless of
# input, so we need to specifically encode all the results to avoid this
# bug.  Python 2.7 doesn't have this problem.
safe_split = lambda a: [ b.decode( 'utf-8' ) for b in _split( a.encode( 'utf-8' ) ) ]


def get_parser():
    parser = ArgumentParser( prefix_chars=':')

    subs = parser.add_subparsers(dest="subparser")

    column_parser = subs.add_parser('include', prefix_chars=':' )
    column_parser.add_argument( '::folders', action='store_true', default=False,  )
    column_parser.add_argument( '::documents',  action='store_true', default=False  )

    display_parser = subs.add_parser( 'display', prefix_chars=':' )
    display_parser.add_argument( '::border',     action='store_true', dest="border", default=False )
   
    return parser

class OGoIndexTableProcessor(markdown.blockprocessors.BlockProcessor):
    """ Present an index of available folders and documents """

    def test(self, parent, block):
        rows = [ row.strip() for row in block.split( '\n' ) ]
        result =  ( len( rows ) > 2 and
                 rows[ 0 ].startswith( '{OGoIndexTable{' ) and
                 rows[ -1 ].endswith( '}OGoIndexTable}' ) )
        return result
        
    def lookup_index_document_from_folder( self, folder ):
        target = self.context.run_command( 'folder::ls', folder=folder, name='index.markdown' )
        if target:
            return target[ 0 ]
        target = self.context.run_command( 'folder::ls', folder=folder, name='index.txt' )
        if target:
            return target[ 0 ]
        return None    

    def run(self, parent, blocks):
        parser = get_parser( )

        """ Parse a table block and build table. """
        block = blocks.pop(0).split('\n')
        datum = block[ 1 : -1 ]
        # parse datum
        border = False
        include_documents = False
        include_folders = False
        for line in datum:
            line = safe_split( line )
            args = parser.parse_args( line )
            if args.subparser == 'display':
                border = args.border            
            if args.subparser == 'include':
                include_documents = args.documents
                include_folders = args.folders
        # Build table
        table = etree.SubElement(parent, 'table')
        if border:
            table.set( 'border', '1' )
        thead = etree.SubElement( table, 'thead' )
        
        # execute query
        search_result = [ ]
        for entity in self.context.run_command( 'folder::ls', folder=self.folder ):
            if entity.object_id == self.document.object_id:
                # do not include ourselves
                continue
            elif isinstance( entity, Folder ) and include_folders:                    
                index = self.lookup_index_document_from_folder( entity )
                if index:
                    search_result.append( ( entity.name, index ))
            elif isinstance( entity, Document ) and include_documents:
                search_result.append( ( entity.abstract, entity ) )
        
        # build header
        self._header_row( thead, border )
        tbody = etree.SubElement( table, 'tbody' )
        # build rows
        for record in search_result:
            self._result_row( record, tbody, border )

    def _header_row(self, parent, border):
        tr = etree.SubElement(parent, 'tr')
        tag = 'th'
        for column in [ 'Title', 'Revision', 'Last Modified' ]:
            c = etree.SubElement(tr, tag)
            c.text = column

    def _result_row(self, record, parent, border):
        """ Given a row of text, build table cells. """
        tr = etree.SubElement(parent, 'tr')
        
        c = etree.SubElement(tr, 'td' )
        a = etree.SubElement( c, 'a' )
        a.text = record[ 0 ]
        a.set( 'class', 'document-link' )
        a.set( 'href', 'OGo#{0}'.format( record[ 1 ].object_id ) )

        c = etree.SubElement(tr, 'td' )
        c.set( 'align', 'center' )
        if record[ 1 ].version_count:
            c.text = unicode( record[ 1 ].version_count )

        c = etree.SubElement(tr, 'td' )
        c.set( 'align', 'center' )
        if record[ 1 ].version_count:
            c.text = unicode( record[ 1 ].version_count )

        c = etree.SubElement(tr, 'td' )
        c.set( 'align', 'center' )
        if record[ 1 ].modified:
            c.text = record[ 1 ].modified.strftime( '%Y-%m-%d' )


class OGoIndexTableExtension(markdown.Extension):

    def __init__(self, configs):
        self.context          = configs.get( 'context', None )
        self.current_folder   = configs.get( 'folder', None )
        self.current_document = configs.get( 'document', None )

    def extendMarkdown(self, md, md_globals):
        """ Add an instance of TableProcessor to BlockParser. """
        ext = OGoIndexTableProcessor(md.parser)
        ext.context = self.context
        ext.folder = self.current_folder
        ext.document = self.current_document
        md.parser.blockprocessors.add('ogoindextable', ext, '<hashheader')


def makeExtension(configs={}):
    return OGoIndexTableExtension(configs=configs)
