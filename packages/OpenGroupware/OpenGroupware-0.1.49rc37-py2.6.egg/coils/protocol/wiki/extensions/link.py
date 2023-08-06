#
# Copyright (c) 2012, 2013
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
import markdown, urllib2
from markdown.util import etree
from coils.core import Task, Project, Folder, Document

class OGoLinksTreeProcessor(markdown.treeprocessors.Treeprocessor):

    def lookup_index_document_from_folder( self, folder ):
        target = self.context.run_command( 'folder::ls', folder=folder, name='index.markdown' )
        if target:
            return target[ 0 ]
        target = self.context.run_command( 'folder::ls', folder=folder, name='index.txt' )
        if target:
            return target[ 0 ]
        return None

    def lookup_index_document_from_project( self, project ):
        return self.lookup_index_document_from_folder( project.folder )

    def void_the_link(self, link ):
        link.text = self.markdown.htmlStash.store( '<s>{0}</s>'.format( link.text ), safe=True )
        link.attrib[ 'href' ] = ''

    def form_label_from_entity(self, entity):
        return 'OGo#{0}'.format( entity.object_id )

    def style_link_from_entity(self, link, entity):
        styles = [ ]
        if isinstance( entity, Task ):
            if entity.state == '00_created':      styles.append( 'task-created' )
            elif entity.state == '30_archived':   styles.append( 'task-archived' )
            elif entity.state == '20_processing': styles.append( 'task-processing' )
            elif entity.state == '30_archived':   styles.append( 'task-archived' )
            elif entity.state == '20_processing': styles.append( 'task-processing' )
            elif entity.state == '02_rejected':   styles.append( 'task-rejected' )
            elif entity.state == '25_done':       styles.append( 'task-done' )
            if entity.owner_id == self.context.account_id:  styles.append( 'task-owner' )
            if entity.creator_id == self.context.account_id:  styles.append( 'task-creator' )
            if entity.executor_id in ( self.context.context_ids ):  styles.append( 'task-executor' )
            # TODO: Add a style for Overdue
            # TODO: Add a style for Current
            # TODO: Add a style for Upcoming
        if styles:
            link.attrib[ 'class' ] = ' '.join( styles )

    def process(self, tic):
        for child in tic.getchildren():
            if child.tag == 'a':

                link_target = child.attrib[ 'href' ]
                link_label  = child.text

                if ( link_target.startswith( 'https://' ) or
                     link_target.startswith( 'http://' ) or
                     link_target.startswith( '#' ) ):
                    continue

                if link_target.lower( ).startswith( 'ogo#' ):
                    link_target = link_target.split( '#' )[ 1 ]
                    if link_target.isdigit( ):
                        object_id = long( link_target )
                        if object_id in self.entity_cache:
                            entity = self.entity_cache[ object_id ]
                        else:
                            entity = self.context.type_manager.get_entity( object_id)
                        if entity:
                            if isinstance( entity, Project ):
                                entity =  self.lookup_index_document_from_project( entity )
                                if entity:
                                    child.set( 'href',  '/wiki/{0}'.format( object_id ) )
                                else:
                                    self.void_the_link( child )
                            else:
                                child.set( 'href',  '/wiki/{0}'.format( object_id ) )
                            #self.style_link_from_entity( child, entity )
                            if child.text == '':
                                child.text = self.form_label_from_entity( entity )
                        else:
                            self.void_the_link( child )

                elif link_target.lower( ).startswith( 'project:' ):
                    # TODO: Implement linking to a project by number
                    name =  urllib2.unquote( link_target[ 8: ] )
                    if name == '.':
                        project = self.current_document.project
                    elif name == '..':
                        # This produces an instrumented list not a project entity
                        # BUG! BROKEN!
                        # TODO: Fix this
                        project = self.current_document.project
                        if project.project:
                            project = project.project
                    else:
                        project = self.context.run_command( 'project::get', number = name )
                    if project:
                        document = self.lookup_index_document_from_project( project ) 
                        if document:
                            child.set( 'href', '{0}'.format( document.object_id ) )
                        else:
                            self.void_the_link( child )
                    else:
                        self.void_the_link( child )

                elif link_target.lower( ).startswith( 'folder:' ):
                    name = urllib2.unquote( link_target[ 7: ] )
                    if name == '.':
                        target = self.lookup_index_document_from_folder( self.current_folder )
                        child.set( 'href', '{0}'.format( target.object_id ) )
                    elif name == '..':
                        target = self.current_folder.folder
                        if not target:
                            target = self.current_folder.project
                        child.set( 'href', '{0}'.format( target.object_id ) )
                    else:
                        self.void_the_link( child )

                elif self.current_folder:
                    document = self.context.run_command( 'folder::ls', name=link_target, folder=self.current_folder )
                    if not document:
                        if '.' not in link_target:
                            document = self.context.run_command( 'folder::ls', name='{0}.markdown'.format( link_target ), folder=self.current_folder )
                            if not document:
                                document = self.context.run_command( 'folder::ls', name='{0}.txt'.format( link_target ), folder=self.current_folder )
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
        self.entity_cache     = configs.get( 'cache', { } )
        self.current_document = configs.get( 'document', None )

    def extendMarkdown(self, md, md_globals):
        ogoext = OGoLinksTreeProcessor( md )
        ogoext.context = self.context
        ogoext.entity_cache = self.entity_cache
        ogoext.current_folder = self.current_folder
        ogoext.current_document = self.current_document
        md.treeprocessors.add("ogo", ogoext, "_end")


def makeExtension(configs={}):
    return OGoLinksExtension( configs=configs )
