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
#
from sqlalchemy          import and_
from coils.core          import Enterprise, Contact, ACL, \
                                AccessForbiddenException, \
                                OGO_ROLE_SYSTEM_ADMIN, \
                                OGO_ROLE_WORKFLOW_ADMIN, \
                                OGO_ROLE_WORKFLOW_DEVELOPERS, \
                                OGO_ROLE_DATA_MANAGER
from coils.core.logic    import ActionCommand
from coils.core.xml      import Render as XML_Render

def yield_enterprises( ctx, context_id ):

    db = ctx.db_session()
    q = db.query( Enterprise.object_id ).\
           join( ACL ).\
           filter( and_( ACL.context_id == context_id, ACL.action == 'allowed', ) ).\
           yield_per( 500 ).\
           enable_eagerloads( False )
    ids = [ ]
    for c in q.all( ):
        ids.append(c[0])
        if len(ids) > 25:
            yield ctx.run_command('enterprise::get', ids=ids)
            del ids[:]
    if ids:
        yield ctx.run_command('enterprise::get', ids=ids)

class CompanyListAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "list-companies"
    __aliases__   = [ 'listCompanies', 'listCompaniesAction' ]

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_mimetype(self):
        return 'application/xml'

    @property
    def result_encoding(self):
        return 'utf8'

    def do_action(self):

        if not self._ctx.has_role( OGO_ROLE_SYSTEM_ADMIN ):
            if self._context_id not in self._ctx.context_ids:
                raise AccessForbiddenException( 'Attempt to perform a list operation on a context not owned.' )

        namespaces = { '': 'http://www.opengroupware.us/model' }

        self.log_message( 'starting stream....' )

        with XML_Render.open_stream( self.wfile, indent=False ) as xml:

            counte = 0

            self.log_message( 'Commenceing yield of contextId#{0}'.format( self._context_id ) )

            for x in yield_enterprises( self._ctx, self._context_id ):
                for e in x:
                    self.log_message( 'Rendering OGo#{0} [Enterprise] (bankCode: {1})'.format( e.object_id, e.bank_code ), category='debug' )
                    XML_Render.render_entity( e, self._ctx, detail_level = self._enterprise_detail, container=xml )
                    countc = 0
                    for contact in self._ctx.r_c( 'enterprise::get-contacts', enterprise=e ):
                        XML_Render.render_entity( contact, self._ctx, detail_level =  self._contact_detail , container=xml )
                        countc += 1
                    self.log_message( '{0} contacts rendered in enterprise'.format( countc ), category='debug' )
                counte += len( x )
            self.log_message( '{0} enterprises rendered'.format( counte ), category='debug' )

    def check_run_permissions(self):
        if ( self._ctx.has_role( OGO_ROLE_SYSTEM_ADMIN ) or
             self._ctx.has_role( OGO_ROLE_WORKFLOW_ADMIN ) or
             self._ctx.has_role( OGO_ROLE_WORKFLOW_DEVELOPERS ) or
             self._ctx.has_role( OGO_ROLE_DATA_MANAGER ) ):
            return
        raise AccessForbiddenException( 'Context lacks role; cannot create workflow routes.' )

    @property
    def result_mimetype(self):
        return 'application/xml'

    def parse_action_parameters(self):

        CONTACT_DETAIL_LEVEL = 8 + 512 + 8192 + 32768
        ENTERPRISE_DETAIL_LEVEL = 8 + 256 + 8192 + 32768

        self._contact_detail    = self.action_parameters.get( 'contactDetailLevel', str( CONTACT_DETAIL_LEVEL ) )
        self._contact_detail    = int( self.process_label_substitutions( self._contact_detail ) )
        self._enterprise_detail = self.action_parameters.get( 'enterpriseDetailLevel', str( ENTERPRISE_DETAIL_LEVEL ) )
        self._enterprise_detail = int( self.process_label_substitutions( self._enterprise_detail ) )
        self._context_id        = self.action_parameters.get( 'contextId', str( self._ctx.account_id ) )
        self._context_id        = int( self.process_label_substitutions( self._context_id ) )

    def do_epilogue(self):
        pass
