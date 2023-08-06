#
# Copyright (c) 2011 Morrison Industries
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
import base64
from datetime            import datetime, tzinfo, date
from coils.core          import CoilsException, fix_microsoft_text, BLOBManager, UniversalTimeZone
from api                 import BEBAPI


DOCUMENT_QUOTE_STATUS        = "Q"
DOCUMENT_ACKNOWLEDE_STATUS   = "A"
DOCUMENT_INVOICE_STATUS      = "I"
PROPERTY_KEY_TRANSCODE       = { 'bankcode':       'bankCode',
                                 'quoteid':        'quoteId',
                                 'salesperson':    'salesperson',
                                 'enterpriseid':   'enterpriseId',
                                 'contactid':      'contactId',
                                 'probablity':     'probablity',
                                 'creationdate':   'creationDate',
                                 'created':        'creationDate',
                                 'expires':        'expireDate',
                                 'expiresdate':    'expireDate',
                                 'expiredate':     'expireDate',
                                 'itaclass':       'itaClass',
                                 'make':           'make',
                                 'model':          'model',
                                 'quantity':       'quantity',
                                 'sellprice':      'sellPrice',
                                 'modelprice':     'modelPrice',
                                 'factoryoptions': 'factoryOptions',
                                 'freight':        'freight',
                                 'taxes':          'taxes',
                                 'tradein':        'tradeIn',
                                 'dealeroptions':  'dealerOptions',
                                 'capacity':       'capacity',
                                 'status':         'status',
                                 'invoicenumber':  'invoiceNumber',
                                 'serialnumbers':  'serialNumbers' }

class DocumentAPI(BEBAPI):

    def _verify_arguements(self, args):

        if (len(args) != 3):
            raise CoilsException('document.store expects three parameters')

        # Parameter 1 - Dict : Document Propeties (set "properties")
        if not isinstance(args[0], dict):
            raise CoilsException('First parameter of document.store must be a dictionary')
        else:
            properties = { }
            for key, value in args[0].items():
                if value:
                    if key.lower() in PROPERTY_KEY_TRANSCODE:
                        properties[PROPERTY_KEY_TRANSCODE[key.lower()]] = value
                    else:
                        properties[key] = value
            # Properties "bankCode", "enterpriseId", "quoteId", and "status" are always required
            if 'bankCode' not in properties:
                raise CoilsException('First parameter parameter dictionary must contain the attribute "bankCode"')
            if 'enterpriseId' not in properties:
                raise CoilsException('First parameter parameter dictionary must contain the attribute "enterpriseId"')
            if 'quoteId' not in properties:
                raise CoilsException('First parameter parameter dictionary must contain the attribute "quoteId"')
            if 'status' not in properties:
                raise CoilsException('First parameter parameter dictionary must contain the attribute "status"')
            # Making sure "enterpriseId", "contactId" are integers and "bankCode" is uppercase and stripped.
            for key, value in properties.items():
                if key == 'enterpriseId':
                    properties['enterpriseId'] = int(value)
                elif key == 'contactId':
                    properties['contactId'] = int(value)
                elif key == 'bankCode':
                    properties['bankCode'] = value.strip().upper()
                elif key == 'make':
                    properties['make'] = value.strip().upper()
                elif key == 'model':
                    properties['model'] = value.strip().upper()
                elif key == 'creationDate':
                    properties['creationDate'] = datetime.strptime(value, '%Y-%m-%d').date()
                elif key in ('expireDate'):
                    properties['expireDate'] = datetime.strptime(value, '%Y-%m-%d').date()
                else: properties[key] = value

        # Parameter 2 - String : Document Payload
        if not isinstance(args[1], basestring):
            raise CoilsException('Second parameter of document.store must be a string: document')
        payload = args[1]

        # Parameter 3 - String : Search Scope (set "context_ids")
        if not isinstance(args[2], basestring):
            raise CoilsException('Third parameter of document.store must be a string: scope')
        else:
            contexts = self.translate_context_specification(args[2])

        return properties, payload, contexts

    def _lookup_project(self, enterprise_id, contexts):
        project = None
        enterprise = self.context.run_command('enterprise::get', id=enterprise_id, contexts=contexts)
        if enterprise:
            kind = self.protocol_defaults.get('ProjectType', 'MI.FINANCIAL')
            projects = self.context.run_command('enterprise::get-projects', enterprise=enterprise,
                                                                             kind=kind)
            if projects:
                # TODO: Generate administrative notice if there is more than one project of this kind
                project = projects[0]

            else:

                admin_team          = self.protocol_defaults.get('AdministrativeTeam', None)
                admin_permissions   = self.protocol_defaults.get('AdministrativePermissions', None)
                default_permissions = self.protocol_defaults.get('DefaultProjectPermissions', "rwld")

                # Create project, set property, and assign enterprises
                if enterprise.bank_code:
                    project = self.context.run_command('project::new', values={ 'name': '{0}: Financial Folio'.format(enterprise.bank_code),
                                                                                'kind': kind } )
                    self.context.property_manager.set_property(project, 'http://opengroupware.us/financial', 'bankCode', enterprise.bank_code)
                else:
                    project = self.context.run_command('project::new', values={ 'name': '{0}: Financial Folio'.format(enterprise.object_id),
                                                                                'kind': kind } )
                self.context.run_command('project::set-enterprises', project=project, enterprises=[enterprise])

                # Apply the specified default permissions for each of the current contexts
                for context_id in contexts:
                    self.context.run_command('object::set-acl', object=project,
                                                                context_id=context_id,
                                                                permissions=default_permissions)

                # If an admin team is specified apply the admin permissions for that team
                if admin_team:
                    if (isinstance(admin_team, basestring)):
                        if admin_team.isdigit():
                            admin_team = int(admin_team)
                        else:
                            raise CoilsException('Admin team specified for project creation is non-numeric')
                    self.context.run_command('object::set-acl', object=project, context_id=admin_team, permissions=default_permissions)

        return project

    def api_document_store(self, args):

        # Verify arguements
        properties, payload, contexts = self._verify_arguements(args)

        # Process
        project = self._lookup_project(properties['enterpriseId'], contexts)
        if not project:
            raise CoilsException('Unable to marshal document storage project for enterpriseId#{0} (contexts={1})'.\
                                  format(properties['enterpriseId'], contexts))


        if properties['status'] == DOCUMENT_QUOTE_STATUS:
            folder_path = '/Quotes'
            kind = 'QUOTE'
        elif properties['status'] == DOCUMENT_ACKNOWLEDE_STATUS:
            folder_path = '/Acknowledgements'
            kind = 'ACKNOWLEDGEMENT'
        elif properties['status'] == DOCUMENT_INVOICE_STATUS:
            folder_path = '/Invoices/{0}'.format(properties['date'].strftime('%Y/%m'))
            kind = 'INVOICE'
        else:
            raise CoilsException('Do not understand status code "{0}".'.format(properties['status']))

        folder = self.context.run_command('project::get-path', path=folder_path,
                                                            project=project,
                                                            create=True)
        if (folder is None):
            raise CoilsException('Unable to create folder "{0}" in {1}'.format(folder_path, project))

        content_stream  = BLOBManager.ScratchFile()
        content_stream.write(base64.decodestring(args[1]))
        content_stream.seek(0)
        document_name = '{0}.doc'.format(properties['quoteId'])

        # Grab a reference to the property manager
        pm = self.context.property_manager
        documents = self.context.run_command('folder::ls', id=folder.object_id, name=document_name)
        if documents:
            # Document found, we are assuming we are updating the first document
            document = documents[0]
            self.context.run_command('document::set', object=document,
                                                      values = {  },
                                                      handle = content_stream)
        else:
            # Document not found at path, create a new document
            document = self.context.run_command('document::new', name    = document_name,
                                                                 values  = { },
                                                                 project = project,
                                                                 folder  = folder,
                                                                 handle  = content_stream)

        # Store properties
        pm = self.context.property_manager
        namespace = 'http://www.opengroupware.us/bebrpc'
        for key, value in properties.items():
            if key == 'salesperson':
                # TODO: How best to translate the salesperson value
                pass
            elif key == 'serialNumbers':
                # TODO: How best to encode this multi-valued field?
                pass
            else:
                pm.set_property(document, namespace, key, value)

        # Manage object links
        if 'contactId' in properties:
            contact = self.context.run_command('contact::get', id = properties['contactId'])
            if contact:
                if not self.context.link_manager.links_between(document, contact):
                    self.context.link_manager.link(contact, document,
                                                   kind='OGo.BEB.Document',
                                                   label='BEB {0} {1}'.format(kind, properties['quoteId']))

        if 'enterpriseId' in properties:
            enterprise = self.context.run_command('enterprise::get', id = properties['enterpriseId'])
            if enterprise:
                if not self.context.link_manager.links_between(document, enterprise):
                    self.context.link_manager.link(enterprise, document,
                                                   kind='OGo.BEB.Document',
                                                   label='BEB {0} {1}'.format(kind, properties['quoteId']))

        self.context.commit()
        return document.object_id






