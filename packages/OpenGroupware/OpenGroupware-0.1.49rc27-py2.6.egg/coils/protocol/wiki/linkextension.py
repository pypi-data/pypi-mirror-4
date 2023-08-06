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

class OGoLinksTreeProcessor(markdown.treeprocessors.Treeprocessor):

    def void_the_link(self, link ):
        link.text = self.markdown.htmlStash.store( '<s>{0}</s>'.format( link.text ), safe=True )
        link.attrib[ 'href' ] = ''

    def process(self, tic):
        for child in tic.getchildren():
            if child.tag == 'a':

                link_target = child.attrib[ 'href' ]
                link_label  = child.text

                if link_target.startswith( 'https://' ) or link_target.startswith( 'http://' ):
                    continue

                if link_target.lower( ).startswith( 'ogo#' ):
                    link_target = link_target.split( '#' )[ 1 ]
                    if link_target.isdigit( ):
                        object_id = long( link_target )
                        entity = self.context.type_manager.get_entity( object_id )
                        if entity:
                            child.attrib[ 'href' ] = '/wiki/{0}'.format( object_id )
                        else:
                            self.void_the_link( child )

                if link_target.lower( ).startswith( 'project:' ):
                    # TODO: Implement linking to a project by number
                    pass

                elif self.current_folder:
                    if len( link_target.split( '.' ) )== 1:
                        link_target = '{0}.txt'.format( link_target )
                    document = self.context.run_command( 'folder::ls', name=link_target, folder=self.current_folder )
                    if document:
                        child.attrib[ 'href' ] = '/wiki/{0}'.format( document[0].object_id )
                    else:
                        self.void_the_link( child )
            else:
                self.process( child )

    def run(self, doc):
        self.process( doc )


class OGoLinksExtension(markdown.Extension):
    def __init__(self, configs):
        self.context          = configs.get( 'context', None )
        self.current_folder   = configs.get( 'folder', None )
        self.current_document = configs.get( 'document', None )

    def extendMarkdown(self, md, md_globals):
        ogoext = OGoLinksTreeProcessor( md )
        ogoext.context = self.context
        ogoext.current_folder = self.current_folder
        ogoext.current_document = self.current_document
        md.treeprocessors.add("ogo", ogoext, "_end")


def makeExtension(configs={}):
    return OGoLinksExtension( configs=configs )
