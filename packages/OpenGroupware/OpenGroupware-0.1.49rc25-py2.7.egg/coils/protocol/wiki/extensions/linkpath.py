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
import markdown
from markdown.util import etree
from coils.core import Folder, Document


class OGoLinkPathProcessor(markdown.blockprocessors.BlockProcessor):
    """ Present an index of available folders and documents """

    def test(self, parent, block):
        rows = [ row.strip() for row in block.split( '\n' ) ]
        result =  ( len( rows ) == 1 and
                 rows[ 0 ].startswith( '{OGoLinkPath{' ) and
                 rows[ 0 ].endswith( '}OGoLinkPath}' ) )
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

        block = blocks.pop(0)

        p = etree.SubElement(parent, 'p')

        records = [ ]

        folder = self.folder
        target = self.lookup_index_document_from_folder( folder )
        if target.object_id != self.document.object_id:
            records.insert( 0, ( folder.name, target.object_id ) )
        while target:
            target = None
            if folder.folder_id is not None:
                folder = self.context.run_command( 'folder::get', id=folder.folder_id )
                if folder:
                    target = self.lookup_index_document_from_folder( folder )
                    if target:
                        if folder.folder_id:
                            records.insert( 0, ( folder.name, target.object_id ) )
                        else:
                            # This is the root folder of a project, so it doesn't actually
                            # have a name, we want to use the name of the project.
                            if folder.project:
                                records.insert( 0, ( folder.project.number, target.object_id ) )
                            else:
                                records.insert( 0, ( 'Project Root', target.object_id ) )
        for record in records:
            a = etree.SubElement( p, 'a' )
            a.text = record[ 0 ]
            a.set( 'class', 'document-link' )
            a.set( 'href', 'OGo#{0}'.format( record[ 1 ] ) )


class OGoLinkPathExtension(markdown.Extension):

    def __init__(self, configs):
        self.context        = configs.get( 'context', None )
        self.current_folder = configs.get( 'folder', None )
        self.current_document = configs.get( 'document', None )


    def extendMarkdown(self, md, md_globals):
        """ Add an instance of TableProcessor to BlockParser. """
        ext = OGoLinkPathProcessor(md.parser)
        ext.context = self.context
        ext.folder = self.current_folder
        ext.document = self.current_document
        md.parser.blockprocessors.add( 'ogolinkpath', ext, '<hashheader' )


def makeExtension(configs={}):
    return OGoLinkPathExtension(configs=configs)
