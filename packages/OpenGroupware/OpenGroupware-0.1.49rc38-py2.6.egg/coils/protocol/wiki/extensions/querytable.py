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
import datetime
from argparse import ArgumentParser
from shlex import split as _split
import markdown
from markdown.util import etree

# shlex's split is broken in regards to Unicode in late Python 2.5 and
# most of Python 2.6.x.  It will turn everyting into UCS-4 regardless of
# input, so we need to specifically encode all the results to avoid this
# bug.  Python 2.7 doesn't have this problem.
safe_split = lambda a: [ b.decode( 'utf-8' ) for b in _split( a.encode( 'utf-8' ) ) ]

def get_parser():
    parser = ArgumentParser( prefix_chars=':')

    subs = parser.add_subparsers(dest="subparser")

    column_parser = subs.add_parser('column', prefix_chars=':' )
    column_parser.add_argument( '::title', action='store', type=str,  )
    column_parser.add_argument( '::alignment',  action='store', choices=[ 'right', 'left', 'center', ],  )
    column_parser.add_argument( '::link',  action='store_true', default=False,  )
    column_parser.add_argument( '::attribute',  action='store', type=str,  )
    column_parser.add_argument( '::format',  action='store', type=str, default='%Y-%m-%d'  )

    entity_parser = subs.add_parser( 'entity', prefix_chars=':'  )
    entity_parser.add_argument( '::kind',     type=str, default='Task',  )

    display_parser = subs.add_parser( 'display', prefix_chars=':' )
    display_parser.add_argument( '::border',     action='store_true', dest="border", default=False )

    query_parser = subs.add_parser( 'query', prefix_chars=':' )
    query_parser.add_argument( '::expression', action='store', choices=[ 'equals', 'gt', 'lt', 'notequals', 'like', 'ilike' ], default='equals',  )
    query_parser.add_argument( '::key',        action='store', dest='key',  )
    query_parser.add_argument( '::value',      action='store', dest='value',  )

    return parser

class OGoQueryTableProcessor(markdown.blockprocessors.BlockProcessor):
    """ Process OGo Queries """

    def test(self, parent, block):
        rows = [ row.strip() for row in block.split( '\n' ) ]
        result =  ( len( rows ) > 2 and
                 rows[ 0 ].startswith( '{OGoQueryTable{' ) and
                 rows[ -1 ].endswith( '}OGoQueryTable}' ) )
        return result

    def run(self, parent, blocks):

        parser = get_parser( )

        """ Parse a table block and build table. """
        block = blocks.pop(0).split('\n')
        datum = block[ 1 : -1 ]
        # parse datum
        border = False
        criteria  =  [ ]
        columns   =  [ ]
        for line in datum:
            line = safe_split( line )
            args = parser.parse_args( line )
            if args.subparser == 'column':
                columns.append( args )
            elif args.subparser == 'query':
                if isinstance( args.value, basestring ):
                    # Allow for inlined variables in the query, we support:
                    #   $__projectid__;  : The project id of the current document
                    #   $__objectid__;   : The object id of the current document
                    #   $__folderid__;   : The folder id of the current document
                    #   $__ownerid__;    : The document owner's object id
                    #   $__userid__;     : The object id of the current user
                    #   $__login__;      : The login (string) of the current user
                    if args.value.startswith( '$__') and args.value.endswith( '__;' ):
                        tmp = args.value[ 3 : -3 ].lower( )
                        if tmp == 'projectid':  args.value = self.current_document.project_id
                        elif tmp == 'objectid': args.value = self.current_document.object_id
                        elif tmp == 'folderid': args.value = self.current_document.folder_id
                        elif tmp == 'onwerid':  args.value = self.current_document.owner_id
                        elif tmp == 'userid':  args.value = self.context.account_id
                        elif tmp == 'login':  args.value = self.context.login
                criteria.append( { 'key': args.key,
                                   'expression': args.expression,
                                   'conjunction': 'AND',
                                   'value': args.value } )
            elif args.subparser == 'entity':
                kind = args.kind.lower( )
            elif args.subparser == 'display':
                border = args.border
        # Build table
        table = etree.SubElement(parent, 'table')
        if border:
            table.set( 'border', '1' )
        thead = etree.SubElement( table, 'thead' )
        # execute query
        search_result = self.context.run_command( '{0}::search'.format( kind ), criteria=criteria, limit=1024 )
        # build header
        self._header_row( thead, columns, border )
        tbody = etree.SubElement( table, 'tbody' )
        # build rows
        for entity in search_result:
            if entity.object_id not in self.entity_cache:
                self.entity_cache[ long( entity.object_id ) ] = entity
            self._result_row( entity, tbody, columns, border )

    def _header_row(self, parent, columns, border):
        tr = etree.SubElement(parent, 'tr')
        tag = 'th'
        for column in columns:
            c = etree.SubElement(tr, tag)
            c.text = column.title

    def _result_row(self, entity, parent, columns, border):
        """ Given a row of text, build table cells. """
        tr = etree.SubElement(parent, 'tr')
        tag = 'td'
        for column in columns:
            c = etree.SubElement(tr, tag)
            try:
                value = getattr( entity, column.attribute )
                if value is None:
                    value = ''
                    c.set( 'class', 'value-null' )
                elif isinstance( value, list ):
                    value = ','.join( value )
                elif isinstance( value, datetime.datetime ):
                    try:
                        value = value.strftime( column.format )
                    except Exception as e:
                        c.text = "!DATE FORMAT ERROR!"
                        c.set( 'class', 'value-error' )
                elif isinstance( value, basestring ):
                    pass
                else:
                    value = unicode( value )
                if column.link:
                    a = etree.SubElement( c, 'a' )
                    a.text = value
                    a.set( 'href', 'OGo#{0}'.format( entity.object_id ) )
                else:
                    c.text = value
            except Exception as e:
                c.text = "!ERROR!"
                c.set( 'class', 'value-error' )
            c.set( 'align', column.alignment )


class OGoQueryTableExtension(markdown.Extension):

    def __init__(self, configs):
        self.context          = configs.get( 'context', None )
        self.entity_cache     = configs.get( 'cache', { } )
        self.current_folder   = configs.get( 'folder', None )
        self.current_document = configs.get( 'document', None )

    def extendMarkdown(self, md, md_globals):
        """ Add an instance of TableProcessor to BlockParser. """
        ext = OGoQueryTableProcessor(md.parser)
        ext.context = self.context
        ext.entity_cache = self.entity_cache
        ext.current_folder = self.current_folder
        ext.current_document = self.current_document
        md.parser.blockprocessors.add('ogoquerytable', ext, '<hashheader')


def makeExtension(configs={}):
    return OGoQueryTableExtension(configs=configs)

