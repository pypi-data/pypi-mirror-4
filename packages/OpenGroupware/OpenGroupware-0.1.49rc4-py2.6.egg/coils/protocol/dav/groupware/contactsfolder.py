#
# Copyright (c) 2009, 2011 Adam Tauno Williams <awilliam@whitemice.org>
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
import sys, coils.core, time
from StringIO                          import StringIO
from coils.core                        import *
from coils.core.vcard                  import Parser as VCard_Parser
from coils.foundation                  import CTag, Contact
from coils.net                         import DAVFolder, \
                                                DAVObject, \
                                                OmphalosCollection, \
                                                OmphalosObject
from groupwarefolder                   import GroupwareFolder

class ContactsFolder(DAVFolder, GroupwareFolder):
    def __init__(self, parent, name, **params):
        DAVFolder.__init__(self, parent, name, **params)

    def __repr__(self):
        return '<ContactsFolder name="{0}" projectMode="{1}" favoriteMode="{2}"/>'.\
            format(self.name, self.is_project_folder, self.is_favorites_folder)

    def supports_GET(self):
        return False

    def supports_POST(self):
        return False

    def supports_PUT(self):
        return True

    def supports_DELETE(self):
        return True

    def supports_PROPFIND(self):
        return True

    def supports_PROPATCH(self):
        return False

    def supports_MKCOL(self):
        return False

    # PROP: GETCTAG

    def get_property_unknown_getctag(self):
        return self.get_property_caldav_getctag()

    def get_property_webdav_getctag(self):
        return self.get_property_caldav_getctag()

    def get_property_caldav_getctag(self):
        return self.get_ctag()

    def get_ctag(self):
        if (self.is_collection_folder):
            return self.get_ctag_for_collection()
        else:
            return self.get_ctag_for_entity('Person')

    def _load_contents(self):
        if (self.is_project_folder):
            # Project sub-folder (all contacts assigned to the project)
            content = self.context.run_command('project::get-contacts', object=self.entity)
        elif (self.is_favorites_folder):
            # Favorites folder
            content = self.context.run_command('contact::get-favorite')
        else:
            # Load *ALL* available contacts - this could be BIG!
            content = self.context.run_command('contact::list', properties = [ Contact ])
        if (len(content) > 0):
            for contact in content:
                if (contact.carddav_uid is None):
                    self.insert_child(contact.object_id, contact, alias='{0}.vcf'.format(contact.object_id))
                else:
                    self.insert_child(contact.object_id, contact, alias=contact.carddav_uid)
        else:
            self.empty_content()
        return True

    def object_for_key(self, name, auto_load_enabled=True, is_webdav=False):
        if (name == '.ctag'):
            return self.get_ctag_representation(self.get_ctag())
        elif ((name in ('.json', '.ls')) and (self.load_contents())):
            return self.get_collection_representation(name, self.get_children())
        elif (name == '.birthdays.json'):
            results = self.context.run_command('contact::get-upcoming-birthdays')
            return self.get_collection_representation(name, results, rendered=True)
        else:
            if (self.is_collection_folder):
                if (auto_load_enabled): self.load_contents()
                if (self.is_loaded):
                    contact = self.get_child(name)
                    if (contact is not None): location = '/dav/Contacts/{0}'.format(name)
            else:
                # Default mode - if the contact list has been loaded, use it, otherwise
                # do a one-off-query.
                location = None
                if (self.is_loaded):
                    contact = self.get_child(name)
                else:
                    (object_id, payload_format, contact, values) = self.get_contact_for_key(name)
            if (contact is not None):
                return self.get_entity_representation(name, contact, location=location, is_webdav=is_webdav)
        self.no_such_path()

    def apply_permissions(self, contact):

        pass

    def do_PUT(self, name):
        payload = self.request.get_request_payload()
        (object_id, payload_format, contact, payload_values) = self.get_contact_for_key_and_content(name, payload)

        if_etag = self.request.headers.get('If-Match', None)
        if if_etag is None:
            self.log.warn('Client issued a put operation with no If-Match!')
        else:
            # TODO: Implement If-Match test
            self.log.warn('If-Match test not implemented at {0}'.format(self.url))

        if payload_values:

            if object_id is None:

                # Create
                contact = self.context.run_command('contact::new', values=payload_values)
                contact.carddav_uid = name
                self.apply_permissions(contact)

                if self.is_favorites_folder:
                    # Contact is being created in the favorites folder, automatically add favorite status
                    self.context.run_command('contact::add-favorite', id=contact.object_id)

                elif self.is_project_folder:
                    self.context.run_command('project::assign-contact', project=project, 
                                                                        contact_id = object_id )
                    raise NotImplementedException('Creating contacts via a project folder is not implemented.')

                self.context.commit()
                self.request.simple_response(201,
                                             data=None,
                                             mimetype=u'text/x-vcard; charset=utf-8',
                                             headers={ 'Etag':     u'{0}:{1}'.format(contact.object_id, contact.version),
                                                       'Location': '/dav/Contacts/{0}.ics'.format(contact.object_id) } )

            else:

                # Update
                # TODO: Check If-Match
                try:
                    contact = self.context.run_command('contact::set', object=contact,
                                                                       values=payload_values)
                    if self.is_favorites_folder:
                        # Contact is being updated in the favorites folder, automatically add favorite status
                        # This means every update to a favorite contact causes a user defaults rewrite
                        self.context.run_command('contact::add-favorite', id=contact.object_id)

                    elif self.is_project_folder:
                        # TODO: Implement: Update contacts via a project sub-folder
                        self.context.run_command('project::assign-contact', project=project, 
                                                                            contact_id = object_id )

                except Exception, e:
                    self.log.error('Error updating objectId#{0} via WebDAV'.format(object_id))
                    self.log.exception(e)
                    raise e
                else:
                    self.context.commit()
                    self.request.simple_response(204,
                                                 data=None,
                                                 mimetype=u'text/x-vcard; charset=utf-8',
                                                 headers={ 'Etag':     u'{0}:{1}'.format(contact.object_id, contact.version),
                                                           'Location': '/dav/Contacts/{0}.ics'.format(contact.object_id) } )

    def do_DELETE(self, name):

        if (self.is_favorites_folder and (self.load_contents())):
            contact = self.get_child(name)

        else:
            (object_id, payload_format, contact, values) = self.get_contact_for_key(name)

        if (contact is None):
            self.no_such_path()

        try:

            if self.is_favorites_folder:
                # NOTE: Deletion of a contact from a favorite folder does *not* delete
                #       the contact it merely removes the favorite status.
                self.log.debug('Removing favorite status from contactId#{0} for userId#{1}'.\
                    format(contact.object_id, self.context.account_id))
                self.context.run_command('contact::remove-favorite', id=contact.object_id)

            elif self.is_project_folder:
                # NOTE: Deletion of a contact from a projects folder should *not* delete
                #       the contact only unassign the contact from the project.
                self.context.run_command('project::unassign-contact', project=project, 
                                                                      contact_id = object_id )

            else:
                # Delete the contact
                if contact.is_account:
                    self.simple_response(423, message='Account objects cannot be deleted.')
                    return
                    
                self.context.run_command('contact::delete', object=contact)

            self.context.commit()
        except:
            self.request.simple_response(500, message='Deletion failed' )
        else:
            self.request.simple_response(204)

    def do_OPTIONS(self):
        ''' Return a valid WebDAV OPTIONS response '''
        methods = [ 'OPTIONS, GET, HEAD, POST, PUT, DELETE, TRACE, COPY, MOVE',
                    'PROPFIND, PROPPATCH, LOCK, UNLOCK, REPORT, ACL' ]
        self.request.simple_response(200,
                                     data=None,
                                     mimetype=u'text/plain',
                                     headers={ 'DAV':           '1, 2, access-control, addressbook',
                                               'Allow':         ','.join(methods),
                                               'Connection':    'close',
                                               'MS-Author-Via': 'DAV'} )
