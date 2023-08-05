#
# Copyright (c) 2010, 2011 Adam Tauno Williams <awilliam@whitemice.org>
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
import hashlib,urlparse,urllib
from coils.core                        import *
from coils.core.vcard                  import Parser as VCard_Parser
from coils.core.icalendar              import Parser as VEvent_Parser
from coils.net                         import DAVObject, \
                                                DAVFolder, \
                                                OmphalosCollection, \
                                                OmphalosObject, \
                                                StaticObject
from teamobject                        import TeamObject
from taskobject                        import TaskObject
from eventobject                       import EventObject
from contactobject                     import ContactObject

ENTITY_REPRESENTATION_DICT = { 'Appointment': EventObject,
                               'Contact':     ContactObject,
                               'Task':        TaskObject,
                               'Team':        TeamObject }

class GroupwareFolder(object):

    def get_ctag_for_entity(self, entity):
        ''' Return a ctag appropriate for this object.
            Actual WebDAV objects should override this method '''
        db = self.context.db_session()
        query = db.query(CTag).filter(CTag.entity==entity)
        ctags = query.all()
        if (len(ctags) == 0):
            return None
        query = None
        return ctags[0].ctag

    def get_ctag_for_collection(self):
        if (self.load_contents()):
            m = hashlib.md5()
            for entry in self.get_children():
                m.update('{0}:{1}'.format(entry.object_id, entry.version))
            return m.hexdigest()
        return None

    def get_ctag_representation(self, ctag):
        return StaticObject(self, '.ctag', context=self.context,
                                            request=self.request,
                                            payload=ctag,
                                            mimetype='text/plain')

    @property
    def is_favorites_folder(self):
        if (self.parent.__class__.__name__ == 'FavoritesFolder'):
            return True
        return False

    @property
    def is_project_folder(self):
        if (hasattr(self, 'entity')):
            if (self.entity.__entityName__ == 'Project'):
                return True
        return False

    @property
    def is_child_folder(self):
        if (self.parent.__class__ ==  self.__class__):
            return True
        return False

    @property
    def is_collection_folder(self):
        if (self.is_favorites_folder or
            self.is_project_folder or
            self.is_child_folder):
            return True
        return False

    def inspect_name(self, name, default_format='ics'):
        extension = name.split('.')[-1:][0]
        if extension == name: extension = None
        if extension:
            format = extension.lower()
            if format in ( 'ics', 'vjl', 'json', 'xml', 'yaml' ):
                uid = name[ :-len(format) ]
            else:
                format = default_format
                uid = name
        if uid.isdigit( ): 
            numeric = True
        else:
            numeric = False
        if uid.isdigit( ):
            object_id = int( uid )
        else:
            object_id = None
        return ( format, extension, uid, numeric )

    def name_has_format_key(self, name):
        if ((name[-4:] == '.vcf') or
            (name[-5:] == '.json') or
            (name[-4:] == '.xml') or
            (name[-4:] == '.ics') or
            (name[-5:] == '.yaml')):
            return True
        return False

    def get_format_key_from_name(self, name):
        if (name[-4:] == '.vcf'):
            return 'vcf'
        elif (name[-4:] in ('.ics', '.vjl')):
            return 'ics'
        elif (name[-5:] == '.json'):
            return 'json'
        elif (name[-4:] == '.xml'):
            return 'xml'
        elif (name[-5:] == '.yaml'):
            return 'yaml'
        raise NotImplementedException('Unimplemented representation "{0}" encountered.'.format(name))

    def get_dav_form_of_name(self, name, extension='vcf'):
        return '{0}.{1}'.format(self.get_object_id_from_name(name), extension)

    def get_object_id_from_name(self, name):
        parts = name.split('.')
        if (len(parts) == 2):
            if (parts[0].isdigit()):
                return int(parts[0])
        return None

    def name_is_coils_key(self, name):
        parts = name.split('.')
        if (len(parts) == 2):
            if ((self.get_object_id_from_name(name) is not None) and
                (self.name_has_format_key(name))):
                    return True
        return False

    def get_contact_for_key(self, key):
        return self.get_contact_for_key_and_content(key, None)

    def get_contact_for_key_and_content(self, key, payload):
        # If we are PROPFIND'ing the folder we already will have the Contacts listed in
        # the object, so we really don't want to do a one-by-one load.  One caveat is
        # that we will not have the Contact's comment value.  That should probably be
        # fixed in the ORM.
        contact        = None
        object_id      = None
        payload_values = None
        payload_format = None
        if (self.name_is_coils_key(key)):
            #TODO: This is inefficient, key gets parsed three times
            object_id      = self.get_object_id_from_name(key)
            payload_format = self.get_format_key_from_name(key)
        else:
            # We assume the format is vCard if the name was not #######.{format}
            payload_format = 'vcf'
        if (payload is not None):
            if (len(payload) > 15):
                if (payload_format == 'vcf'):
                    payload_values = VCard_Parser.Parse(payload, self.context, entity_name='Contact')
                    if (isinstance(payload_values, list)):
                        payload_values = payload_values[0]
                elif (payload_format == 'json'):
                    # TODO: Implement parsing JSON payload
                    raise NotImplementedException()
                elif (payload_format == 'xml'):
                    # TODO: Implement parsing XML payload
                    raise NotImplementedException()
                elif (payload_format == 'yaml'):
                    # TODO: Implement parsing YAML payload
                    raise NotImplementedException()
                else:
                    raise CoilsException('Format {0} not support for Contact entities'.format(payload_format))
                # Perhaps the vCard contained the object_id? If we don't have an object_id from
                # the name, check the Omphalos values.
                if (object_id is None and
                    payload_values is not None and
                    'object_id' in payload_values):
                    object_id = payload_values.get('object_id')
        if (object_id is not None):
            contact = self.context.run_command('contact::get', id=object_id)
        else:
            contact = self.context.run_command('contact::get', uid=key)
        return (object_id, payload_format, contact, payload_values)

    def get_appointment_for_key(self, key):
        return self.get_appointment_for_key_and_content(key, None)

    def get_appointment_for_key_and_content(self, key, payload):
        appointment    = None
        object_id      = None
        payload_values = None
        payload_format = None
        if (self.name_is_coils_key(key)):
            #TODO: This is inefficient, key gets parsed three times
            object_id      = self.get_object_id_from_name(key)
            payload_format = self.get_format_key_from_name(key)
            appointment = self.context.run_command('appointment::get', id=object_id)
        else:
            # If key is not in ######.ics Coils format we assume it is a CalDAV key
            # and attempt to lookup the appointment using that.  And we assume vEvent
            # (ics) format)
            payload_format = 'ics'
            appointment = self.context.run_command('appointment::get', uid=key)
            if (appointment is not None):
                object_id = appointment.object_id
        if (payload is not None):
            if (len(payload) > 15):
                if (payload_format == 'ics'):
                    # This return value will always be a list
                    payload_values = VEvent_Parser.Parse(payload, self.context)
                    if (len(payload_values) > 0):
                        object_id = payload_values[0].get('object_id', None)
                        if (object_id is not None):
                            payload_values = payload_values[0]
                            appointment = self.context.run_command('appointment::get', id=object_id)
                    #if (isinstance(payload_values, list)):
                    #    payload_values = payload_values[0]
                elif (payload_format == 'json'):
                    # TODO: Implement parsing JSON payload
                    raise NotImplementedException()
                elif (payload_format == 'xml'):
                    # TODO: Implement parsing XML payload
                    raise NotImplementedException()
                elif (payload_format == 'yaml'):
                    # TODO: Implement parsing YAML payload
                    raise NotImplementedException()
                else:
                    raise CoilsException('Format {0} not support for Contact entities'.format(payload_format))
        # object_id: An integer if the values update an existing appointment, otherwise None [creation]
        # payload_format: ics, json, xml, yaml
        # appointment: Existing appointment to receive update, otherwise None
        # payload_values: In the case of an update this value is a dict of the Omphalos values
        #                 In the case of a create this value is a list of Omphalos dicts
        return (object_id, payload_format, appointment, payload_values)

    def get_process_for_key(self, key):
        process        = None
        object_id      = None
        if (self.name_is_coils_key(key)):
            #TODO: This is inefficient, key gets parsed three times
            object_id      = self.get_object_id_from_name(key)
            payload_format = self.get_format_key_from_name(key)
            process = self.context.run_command('process::get', id=object_id)
        # object_id: An integer if the values update an existing appointment, otherwise None [creation]
        # payload_format: ics, json, xml, yaml
        # appointment: Existing appointment to receive update, otherwise None
        # payload_values: In the case of an update this value is a dict of the Omphalos values
        #                 In the case of a create this value is a list of Omphalos dicts
        return (object_id, 'ics', process, None)


    def get_task_for_key(self, key):
        return self.get_task_for_key_and_content(key, None)

    def get_task_for_key_and_content(self, key, payload):
        task           = None
        object_id      = None
        payload_values = None
        payload_format = None
        if (self.name_is_coils_key(key)):
            #TODO: This is inefficient, key gets parsed three times
            object_id      = self.get_object_id_from_name(key)
            payload_format = self.get_format_key_from_name(key)
            task = self.context.run_command('task::get', id=object_id)
        else:
            # If key is not in ######.ics Coils format we assume it is a CalDAV key
            # and attempt to lookup the appointment using that.  And we assume vEvent
            # (ics) format)
            payload_format = 'ics'
            task = self.context.run_command('task::get', uid=key)
            if (task is not None):
                object_id = task.object_id
        if (payload is not None):
            if (len(payload) > 15):
                if (payload_format == 'ics'):
                    # This return value will always be a list
                    payload_values = VEvent_Parser.Parse(payload, self.context)
                    if (len(payload_values) > 0):
                        object_id = payload_values[0].get('object_id', None)
                        if (object_id is not None):
                            payload_values = payload_values[0]
                            task = self.context.run_command('task::get', id=object_id)
                elif (payload_format == 'json'):
                    # TODO: Implement parsing JSON payload
                    raise NotImplementedException()
                elif (payload_format == 'xml'):
                    # TODO: Implement parsing XML payload
                    raise NotImplementedException()
                elif (payload_format == 'yaml'):
                    # TODO: Implement parsing YAML payload
                    raise NotImplementedException()
                else:
                    raise CoilsException('Format {0} not support for Task entities'.format(payload_format))
        # object_id: An integer if the values update an existing task, otherwise None [creation]
        # payload_format: ics, json, xml, yaml
        # task: Existing task to receive update, otherwise None
        # payload_values: In the case of an update this value is a dict of the Omphalos values
        #                 In the case of a create this value is a list of Omphalos dicts
        return (object_id, payload_format, task, payload_values)

    def get_note_for_key_and_content(self, key, payload):
        note           = None
        object_id      = None
        payload_values = None
        payload_format = None
        if (self.name_is_coils_key(key)):
            #TODO: This is inefficient, key gets parsed three times
            object_id      = self.get_object_id_from_name(key)
            payload_format = self.get_format_key_from_name(key)
            note = self.context.run_command('note::get', id=object_id)
        else:
            # If key is not in ######.ics Coils format we assume it is a CalDAV key
            # and attempt to lookup the appointment using that.  And we assume vEvent
            # (ics) format)
            payload_format = 'ics'
            note = self.context.run_command('note::get', uid=key)
            if (note is not None):
                object_id = note.object_id
        if (payload is not None):
            if (len(payload) > 15):
                if (payload_format == 'ics'):
                    # This return value will always be a list
                    payload_values = VEvent_Parser.Parse(payload, self.context)
                    if (len(payload_values) > 0):
                        object_id = payload_values[0].get('object_id', None)
                        if (object_id is not None):
                            payload_values = payload_values[0]
                            note = self.context.run_command('note::get', id=object_id)
                elif (payload_format == 'json'):
                    # TODO: Implement parsing JSON payload
                    raise NotImplementedException()
                elif (payload_format == 'xml'):
                    # TODO: Implement parsing XML payload
                    raise NotImplementedException()
                elif (payload_format == 'yaml'):
                    # TODO: Implement parsing YAML payload
                    raise NotImplementedException()
                else:
                    raise CoilsException('Format {0} not support for Note entities'.format(payload_format))
        # object_id: An integer if the values update an existing task, otherwise None [creation]
        # payload_format: ics, json, xml, yaml
        # task: Existing task to receive update, otherwise None
        # payload_values: In the case of an update this value is a dict of the Omphalos values
        #                 In the case of a create this value is a list of Omphalos dicts
        return (object_id, payload_format, note, payload_values)

    def get_entity_representation(self, name, entity, representation=None,
                                                      is_webdav=False,
                                                      location=None):
        if (not is_webdav):
            if (representation is None):
                representation = self.get_format_key_from_name(name)
        if ((is_webdav) or (representation in ['ics', 'vcf'])):
            # This is a WebDAV / GroupDAV / CalDAV / CardDAV representation
            reprclass = ENTITY_REPRESENTATION_DICT.get(entity.__entityName__, DAVObject)
            return reprclass(self,
                              name,
                              location=location,
                              entity=entity,
                              context=self.context,
                              request=self.request)
        elif (representation in ['json', 'yaml', 'xml']):
            # This is a REST representation
            return OmphalosObject(self,
                                   name,
                                   entity=entity,
                                   context=self.context,
                                   request=self.request)
        else:
            raise CoilsException('Unknown representation requested')

    def get_collection_representation(self, name, collection, rendered=False):
        # Returns an Omphalos representation of the collection;
        # WebDAV does *not* use this; this is for REST support
        return OmphalosCollection(self,
                                   name,
                                   rendered=rendered,
                                   data=collection,
                                   context=self.context,
                                   request=self.request)

    def move_helper(self, name):
        # See Issue#158
        # TODO: Support the Overwrite header T/F
        ''' MOVE /dav/Projects/Application%20-%20BIE/Documents/87031000 HTTP/1.1
            Content-Length: 0
            Destination: http://172.16.54.1:8080/dav/Projects/Application%20-%20BIE/Documents/%5B%5DSheet1
            Overwrite: T
            translate: f
            User-Agent: Microsoft-WebDAV-MiniRedir/6.0.6001
            Host: 172.16.54.1:8080
            Connection: Keep-Alive
            Authorization: Basic YWRhbTpmcmVkMTIz

            RESPONSE
               201 (Created) - Created a new resource
               204 (No Content) - Moved to an existing resource
               403 (Forbidden) - The source and destination URIs are the same.
               409 - Conflict
               412 - Precondition failed
               423 - Locked
               502 - Bad Gateway
            '''

        source = self.object_for_key(name)

        # Get overwrite preference from request
        overwrite = self.request.headers.get('Overwrite', 'F').upper()
        if overwrite == 'T':
            overwrite = True
        else:
            overwrite = False

        # Determine destination
        destination = self.request.headers.get('Destination')
        destination = urlparse.urlparse(destination).path
        destination = urllib.unquote(destination)
        if not destination.startswith('/dav/'):
            raise CoilsException('MOVE cannot be performed across multiple DAV roots')
        destination = destination.split('/', 64)[2:] # The target path with leading /dav/ (the root) discarded
        target_name = destination[-1:][0] # The name of the object to be created
        target_path = destination[:-1] # The path chunks
        destination = None # Free the destination variable

        # Find the target object
        target = self.root
        try:
            for component in target_path:
                target = target.object_for_key(component)
        except:
            # Really?  Shouldn't we do something meaningful?
            pass
        else:
            pass

        self.log.debug('Request to move "{0}" to "{1}" as "{2}".'.format(source, target, target_name))

        return source, target, target_name, overwrite
